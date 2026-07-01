# STARTUP_INVESTIGATION.md

Investigação do startup lento no Render Free (hibernação → primeiro acesso).

---

## 1. Fluxo Real de Startup

```
Container acorda (wake-up do Render)
│
├─ [Dockerfile CMD, linha 37]
│
├── python manage.py migrate --noinput
│     ↓ conecta ao PostgreSQL
│     ↓ consulta tabela django_migrations
│     ↓ aplica migrations pendentes (ou confirma que não há)
│
├── python manage.py import_study_plan
│     ↓ para cada um dos 14 módulos:
│         SELECT Subject WHERE slug=...        (14 queries)
│         UPDATE_OR_CREATE StudyModule         (14 queries)
│         para cada capítulo do módulo:
│             UPDATE_OR_CREATE StudyChapter    (98 queries)
│             chapter.related_subjects.add()  (98 M2M queries)
│     ↓ total: ~224+ queries
│
├── python manage.py populate_chapter_content
│     ↓ lê 14 arquivos MASTER de docs/ do disco
│     ↓ StudyModule.objects.all()             (1 query)
│     ↓ para cada um dos 98 capítulos:
│         StudyChapter.objects.get(...)       (98 queries)
│         chapter.save(update_fields=['content'])  (98 UPDATEs — SEMPRE)
│     ↓ total: ~197 queries + leitura de arquivos
│
├── python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md
│     ↓ lê e faz parsing de arquivo 242 KB / 5.840 linhas
│     ↓ _ensure_subjects: UPDATE_OR_CREATE por disciplina  (~14 queries)
│     ↓ para cada uma das 800 questões:
│         @transaction.atomic (savepoint)
│         Question.objects.select_for_update().first()  (800 queries com lock)
│         → se inalterada: apenas incrementa contador
│         → se nova/alterada: INSERT + bulk_create alternatives
│     ↓ total: 814+ queries, 800 savepoints, parsing de 242 KB
│
├── python manage.py create_admin
│     ↓ lê ADMIN_EMAIL e ADMIN_PASSWORD das env vars
│     ↓ User.objects.filter(email=...).exists()  (1 query)
│     ↓ se já existe: encerra
│
└── gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
      ↓ SOMENTE AQUI o servidor web começa a aceitar requisições
```

---

## 2. Arquivo Responsável

| Arquivo | Linha | Responsável |
|---------|-------|-------------|
| `Dockerfile` | 37–48 | `CMD ["sh", "-c", "..."]` — contém toda a cadeia de startup |
| `Dockerfile` | 34–36 | Comentário explicando a decisão: "No plano free do Render, preDeployCommand não é suportado" |
| `render.yaml` | 25–26 | Confirma a ausência de `preDeployCommand` no plano free |

Não existe `entrypoint.sh`, `start.sh` ou `Procfile`. Todo o fluxo está embutido diretamente no `CMD` do Dockerfile.

---

## 3. O Que Está Sendo Executado

| Comando | Motivo declarado | Frequência real |
|---------|-----------------|----------------|
| `migrate` | Aplicar migrações de banco | **Todo startup** (deploy + wake-up) |
| `import_study_plan` | Popular módulos e capítulos do plano de estudos | **Todo startup** (deploy + wake-up) |
| `populate_chapter_content` | Preencher conteúdo dos 98 capítulos a partir dos MDs | **Todo startup** (deploy + wake-up) |
| `import_questions` | Importar 800 questões do banco mestre | **Todo startup** (deploy + wake-up) |
| `create_admin` | Criar/verificar superusuário admin | **Todo startup** (deploy + wake-up) |

**Frequência real = toda vez que o Render acorda o container**, independentemente de ter havido deploy ou não.

---

## 4. Possíveis Causas Confirmadas

### CAUSA 1 — Comandos de importação executando em todo startup `[CRÍTICO]`

**Descrição:** `import_study_plan`, `populate_chapter_content` e `import_questions` são comandos de seed de dados. Estão posicionados no `CMD` do Dockerfile, que é executado não apenas em deploys mas em toda reinicialização do container — incluindo wake-ups após hibernação.

**Impacto:** Os três comandos juntos somam ~1.230+ queries ao banco, parsing de um arquivo de 242 KB e leitura de 14 arquivos MASTER do disco, **a cada vez que o usuário faz o primeiro acesso**.

**Criticidade:** CRÍTICO

---

### CAUSA 2 — Os comandos executam em todo wake-up, não apenas no deploy `[CRÍTICO]`

**Descrição:** O Render Free hiberna o serviço após inatividade. A cada wake-up, o processo reinicia e executa o `CMD` completo. O comentário no Dockerfile (`# Todos os comandos são idempotentes: seguros de rodar em todo deploy`) revela que a intenção era rodar apenas em deploys, mas o `CMD` não distingue deploy de wake-up.

**Impacto:** O usuário que acessa o site após um período de inatividade aguarda 4–5 minutos porque o container está reprocessando dados que já existem no banco.

**Criticidade:** CRÍTICO

---

### CAUSA 3 — `import_questions` faz 800 transações individuais mesmo quando nada mudou `[ALTO]`

**Descrição:** O método `_upsert_question` (arquivo `apps/questions/services/import_service.py`, linha 118) é decorado com `@transaction.atomic` e executa `select_for_update()` para cada uma das 800 questões, uma a uma. Mesmo quando todas as 800 questões estão inalteradas, o banco recebe 800 savepoints + 800 SELECTs com lock de linha.

**Impacto:** Esta operação é isoladamente a mais cara do startup. Estimativa: 60–150 segundos em banco remoto (Render → PostgreSQL com latência de rede).

**Criticidade:** ALTO

---

### CAUSA 4 — `populate_chapter_content` salva todos os 98 capítulos sem verificar se o conteúdo mudou `[ALTO]`

**Descrição:** No arquivo `apps/study_plan/management/commands/populate_chapter_content.py`, linha 201–202, o código executa `chapter.save(update_fields=['content'])` incondicionalmente para todos os capítulos. Não há comparação entre o conteúdo extraído do arquivo e o conteúdo já armazenado no banco.

**Impacto:** 98 `UPDATE` desnecessários a cada startup, mesmo que nenhum arquivo MASTER tenha mudado. Em banco remoto com latência, cada UPDATE pode levar 20–50ms → ~2–5 segundos extras.

**Criticidade:** ALTO

---

### CAUSA 5 — Build e startup misturados `[MÉDIO]`

**Descrição:** O Dockerfile executa `collectstatic` no build (linha 29–30, correto), mas todas as outras operações de dados ficaram no `CMD`. A distinção entre "o que roda uma vez, no build/deploy" e "o que roda toda vez que o container inicia" não foi implementada.

**Impacto:** Seed de dados sendo re-executado desnecessariamente em cada reinício.

**Criticidade:** MÉDIO

---

### CAUSA 6 — migrate em todo startup `[BAIXO]`

**Descrição:** `python manage.py migrate --noinput` executa em todo startup. Quando não há migrações pendentes, o Django consulta `django_migrations`, confirma que está atualizado e encerra rápido.

**Impacto:** Baixo na prática (~2–5 segundos), pois o Django é eficiente nesta verificação. Mas ainda adiciona uma conexão e query em todo wake-up.

**Criticidade:** BAIXO

---

### CAUSA 7 — create_admin em todo startup `[BAIXO]`

**Descrição:** `create_admin` executa 1 query (`User.objects.filter(email=...).exists()`) e retorna imediatamente se o usuário já existir.

**Impacto:** Desprezível (~100ms).

**Criticidade:** BAIXO

---

## 5. Correções Recomendadas

### Correção 1 (Principal) — Separar seed de startup

**Situação atual:**
```
CMD = migrate + import_study_plan + populate_chapter_content + import_questions + create_admin + gunicorn
Executa: em TODO startup (deploy + wake-up)
```

**Situação recomendada:**
```
CMD = migrate + create_admin + gunicorn
Executa: em TODO startup

"seed de dados" = import_study_plan + populate_chapter_content + import_questions
Executa: apenas quando necessário (primeiro deploy ou quando os dados mudam)
```

Como o Render Free não suporta `preDeployCommand`, a forma recomendada é adicionar uma **verificação de estado** no início de cada comando de seed:

```python
# Exemplo para import_study_plan
expected_count = len(STUDY_PLAN_MAP)
if StudyModule.objects.count() == expected_count:
    self.stdout.write("Plano de estudos já populado — pulando.")
    return
```

```python
# Exemplo para import_questions
total_expected = 800  # ou contar do parser antes de persistir
if Question.objects.count() >= total_expected:
    self.stdout.write("Questões já importadas — pulando.")
    return
```

Esta abordagem mantém a idempotência mas adiciona um "fast path" que custa **1 query de contagem** em vez de centenas de upserts.

---

### Correção 2 — `populate_chapter_content`: verificar antes de salvar

**Situação atual:**
```python
chapter.content = content
chapter.save(update_fields=['content'])  # sempre salva, 98x
```

**Situação recomendada:**
```python
if chapter.content != content:
    chapter.content = content
    chapter.save(update_fields=['content'])
```

Custo passa de **98 UPDATEs** para **98 comparações de string em memória** (quando nada mudou).

---

### Correção 3 — `import_questions`: batch do check de existência

**Situação atual:**
```python
# Para cada uma das 800 questões:
@transaction.atomic
def _upsert_question(self, parsed, subject, report):
    existing = Question.objects.filter(external_id=...).select_for_update().first()
    # 800 savepoints + 800 SELECTs individuais com lock
```

**Situação recomendada:**
```python
# Uma única query antes do loop:
existing_map = {
    q["external_id"]: q["content_hash"]
    for q in Question.objects.values("external_id", "content_hash")
}

# No loop, verificar sem query:
if existing_map.get(parsed.external_id) == parsed.content_hash:
    report.unchanged += 1
    continue  # pula completamente sem abrir transação

# Só abre transação para questões novas ou alteradas
```

Custo passa de **800 transações + 800 SELECTs com lock** para **1 SELECT de todos os IDs/hashes + N transações apenas para novas/alteradas**.

---

## 6. Estimativa de Ganho

### Startup atual (wake-up após hibernação)

| Operação | Queries | Estimativa |
|----------|---------|------------|
| migrate | ~10 | ~3s |
| import_study_plan | ~224 | ~15–30s |
| populate_chapter_content | ~197 | ~15–30s |
| import_questions | 814+ (800 com lock) | ~90–150s |
| create_admin | 1 | ~1s |
| gunicorn boot | — | ~5–10s |
| **Total** | **~1.246+** | **~130–225s (~3–4 min)** |

*(Variação depende da latência Render → PostgreSQL no plano free.)*

### Startup esperado após Correção 1 + 2 + 3 (wake-up)

| Operação | Queries | Estimativa |
|----------|---------|------------|
| migrate | ~10 | ~3s |
| import_study_plan (fast path) | 1 COUNT | ~1s |
| populate_chapter_content (fast path) | 1 COUNT | ~1s |
| import_questions (fast path) | 1 COUNT | ~1s |
| create_admin | 1 | ~1s |
| gunicorn boot | — | ~5–10s |
| **Total** | **~14** | **~12–18s** |

### Comparativo

| Cenário | Tempo estimado |
|---------|----------------|
| Startup atual (wake-up) | 3–5 minutos |
| Após correções (wake-up, dados já no banco) | **15–20 segundos** |
| Após correções (deploy com dados novos) | 60–90 segundos (seed roda de verdade) |

---

*Gerado em 2026-07-01. Nenhum arquivo foi alterado.*
