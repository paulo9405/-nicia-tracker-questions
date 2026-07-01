# Startup Optimization — Fase 1

Documentação da primeira otimização de startup do Nícia Track no Render Free.

---

## Problema identificado

**Fonte:** `STARTUP_INVESTIGATION.md`

O `CMD` do `Dockerfile` executava uma cadeia sequencial de 5 operações em **todo startup** do container — incluindo wake-ups após hibernação do Render Free:

```
migrate
  ↓
import_study_plan       (14 módulos, 98 capítulos, ~224 queries)
  ↓
populate_chapter_content  (98 saves incondicionais, leitura de 14 arquivos MD)
  ↓
import_questions        (parsing de 242 KB, 800 transações individuais com select_for_update)
  ↓
create_admin            (1 query)
  ↓
gunicorn (só então o servidor aceita requisições)
```

Os três comandos de importação são declarados idempotentes — não duplicam dados — mas ainda executavam centenas de queries de verificação e atualização mesmo quando os dados já estavam completamente presentes no banco.

**Resultado observado:** primeiro acesso após hibernação do Render → **3 a 5 minutos de espera**.

---

## Alterações realizadas

Três arquivos modificados — apenas o início do método `handle()` de cada comando:

| Arquivo | Linhas alteradas |
|---------|-----------------|
| `apps/study_plan/management/commands/import_study_plan.py` | Fast path adicionado antes do processamento |
| `apps/study_plan/management/commands/populate_chapter_content.py` | Fast path adicionado antes do processamento |
| `apps/questions/management/commands/import_questions.py` | Import de `Question`, constante `_EXPECTED_QUESTION_COUNT = 800` e fast path |

Nenhum outro arquivo foi modificado.

---

## Estratégia utilizada

Cada comando recebeu uma verificação de estado ao início do `handle()`. A verificação usa 1–2 queries de `COUNT` para checar se os dados esperados já existem. Se sim, o comando retorna imediatamente sem processar nada.

### import_study_plan

```python
expected_modules = len(STUDY_PLAN_MAP)                        # 14
expected_chapters = sum(len(m.chapters) for m in STUDY_PLAN_MAP)  # 98

if (StudyModule.objects.count() >= expected_modules
        and StudyChapter.objects.count() >= expected_chapters):
    self.stdout.write("Plano de estudos já populado — pulando.")
    return
```

**Custo no fast path:** 2 queries (`COUNT StudyModule`, `COUNT StudyChapter`).
**Custo original:** ~224 queries (14 subject SELECTs + 14 module upserts + 98 chapter upserts + 98 M2M adds).

### populate_chapter_content

```python
expected_chapters = len(CHAPTER_MAP)  # 98
populated = StudyChapter.objects.filter(content__gt='').count()

if populated >= expected_chapters:
    self.stdout.write("Conteúdo dos capítulos já populado — pulando.")
    return
```

**Custo no fast path:** 1 query (`COUNT StudyChapter WHERE content != ''`).
**Custo original:** ~197 queries + leitura de 14 arquivos Markdown do disco.

### import_questions

```python
_EXPECTED_QUESTION_COUNT = 800  # constante no topo do arquivo

if not dry_run and Question.objects.count() >= _EXPECTED_QUESTION_COUNT:
    self.stdout.write("Banco de questões já importado — pulando.")
    return
```

**Custo no fast path:** 1 query (`COUNT Question`).
**Custo original:** parsing de 242 KB + 814+ queries (800 `select_for_update` individuais com savepoint).

---

## Cenários cobertos

### Banco completo (wake-up normal após hibernação)

```
migrate (verifica migrations)
  ↓
import_study_plan  → 14 módulos? sim, 98 capítulos? sim → "pulando"  (2 queries)
  ↓
populate_chapter_content → 98 com conteúdo? sim → "pulando"          (1 query)
  ↓
import_questions → 800 questões? sim → "pulando"                     (1 query)
  ↓
create_admin (1 query)
  ↓
gunicorn (inicia em segundos)
```

### Primeiro deploy (banco vazio)

```
migrate (aplica todas as migrations)
  ↓
import_study_plan  → 0 módulos? fast path NÃO ativa → roda completo
  ↓
populate_chapter_content → 0 com conteúdo? fast path NÃO ativa → roda completo
  ↓
import_questions → 0 questões? fast path NÃO ativa → roda completo
  ↓
create_admin
  ↓
gunicorn
```

### Banco parcial — módulos faltando

```
StudyModule.count() = 10 < 14  →  fast path NÃO ativa
import_study_plan roda normalmente (reimporta os 14)
```

### Banco parcial — capítulos sem conteúdo

```
StudyChapter.filter(content__gt='').count() = 90 < 98  →  fast path NÃO ativa
populate_chapter_content roda normalmente (preenche todos os 98)
```

### Banco parcial — questões faltando

```
Question.count() = 750 < 800  →  fast path NÃO ativa
import_questions roda normalmente (importa ou atualiza as 800)
```

### `--dry-run` em import_questions

O fast path só é verificado quando `not dry_run`. Em modo dry_run, o comando sempre executa o processo completo de simulação.

---

## Resultado esperado

### Startup atual (wake-up após hibernação)

| Operação | Queries | Estimativa |
|----------|---------|------------|
| migrate | ~10 | ~3s |
| import_study_plan | ~224 | ~15–30s |
| populate_chapter_content | ~197 | ~15–30s |
| import_questions | 814+ | ~90–150s |
| create_admin | 1 | ~1s |
| gunicorn boot | — | ~5–10s |
| **Total** | **~1.246+** | **~3–5 minutos** |

### Startup otimizado (wake-up após hibernação, dados já no banco)

| Operação | Queries | Estimativa |
|----------|---------|------------|
| migrate | ~10 | ~3s |
| import_study_plan (fast path) | 2 | ~0.2s |
| populate_chapter_content (fast path) | 1 | ~0.1s |
| import_questions (fast path) | 1 | ~0.1s |
| create_admin | 1 | ~1s |
| gunicorn boot | — | ~5–10s |
| **Total** | **~15** | **~10–15 segundos** |

### Primeiro deploy (banco vazio) — sem alteração

O tempo de seed continua igual (~60–90s). A otimização não afeta deploys com banco vazio.

---

## Testes

```
216 passed, 0 failed, 94 warnings in 3.53s
```

Nenhum teste existente foi quebrado. A suíte foi executada integralmente antes e após as alterações.

---

## Riscos e limitações

**1. Contagem como proxy de integridade**
O fast path verifica quantidade, não qualidade. Se os 800 registros existirem com conteúdo corrompido ou desatualizado, o fast path pula e os dados errados permanecem. Para forçar reimportação seria necessário implementar um flag `--force` (não feito nesta fase).

**2. `_EXPECTED_QUESTION_COUNT` hardcoded**
O valor 800 reflete o banco atual. Se novas questões forem adicionadas ao arquivo Markdown e o banco já tiver 800 questões, o fast path pularia a importação das novas. Solução: atualizar a constante ao expandir o banco de questões.

**3. populate_chapter_content não verifica conteúdo correto**
O fast path checa se 98 capítulos têm conteúdo não-vazio, mas não compara se o conteúdo é o mais recente dos arquivos MASTER. Se um arquivo MASTER for editado após a população inicial, o fast path impedirá a atualização. Solução futura: Correção 2 (comparar conteúdo antes de salvar).

---

## Próximos passos

### Correção 2 — `populate_chapter_content`: skip por conteúdo idêntico

Atualmente o comando (quando o fast path não ativa) faz 98 UPDATEs incondicionais. A Correção 2 adicionaria uma comparação antes de cada save:

```python
# Situação atual:
chapter.content = content
chapter.save(update_fields=['content'])

# Situação recomendada:
if chapter.content != content:
    chapter.content = content
    chapter.save(update_fields=['content'])
```

**Impacto esperado:** quando o fast path não ativa (banco parcial ou deploy novo), os capítulos já corretos não recebem UPDATE desnecessário.

### Correção 3 — `import_questions`: batch check de existência

Atualmente o importador (quando o fast path não ativa) faz 800 transações individuais com `select_for_update`. A Correção 3 substituiria por um único SELECT de todos os hashes existentes:

```python
# Uma query antes do loop:
existing_map = {
    q["external_id"]: q["content_hash"]
    for q in Question.objects.values("external_id", "content_hash")
}

# No loop: sem query, sem transação para questões inalteradas:
if existing_map.get(parsed.external_id) == parsed.content_hash:
    report.unchanged += 1
    continue

# Só abre transação para questões novas ou alteradas.
```

**Impacto esperado:** deploy com banco parcial passa de 800 transações para N transações (apenas para questões novas/alteradas), reduzindo drasticamente o tempo de reimportação.

---

*Implementado em 2026-07-01. Nenhum test quebrou. Aguardando validação em produção.*
