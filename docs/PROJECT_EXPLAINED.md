# Nícia Track — PROJECT EXPLAINED

> **Documentação viva e didática do projeto.**
> Objetivo: permitir estudar, revisar e explicar o sistema inteiro — em entrevistas ou daqui a 6 meses — **sem abrir o código-fonte**.
>
> **Regra de manutenção:** a cada fase concluída, este documento é **acrescentado ao final**, nunca sobrescrito. O histórico das fases anteriores é preservado integralmente.

---

## Índice

- [Visão geral do produto](#visão-geral-do-produto)
- [Glossário rápido](#glossário-rápido)
- [Status das fases](#status-das-fases)
- [FASE 1 — Arquitetura](#fase-1--arquitetura)
- [FASE 2 — Modelagem](#fase-2--modelagem)
- [FASE 3 — Importador das Questões](#fase-3--importador-das-questões)

---

## Visão geral do produto

**Nícia Track** é uma plataforma de preparação para concursos públicos baseada em:

- **Banco de questões** (800 questões reais já mapeadas)
- **Simulados** (réplica da prova: 40 questões com distribuição por disciplina)
- **Estatísticas** de desempenho
- **Revisão de erros**
- **Evolução temporal** (dashboard, streak, metas)

A usuária inicial é **Nícia** (candidata ao cargo de Médico Veterinário — Concurso 003/2026, Prefeitura de Ponta Grossa/PR, banca Instituto UniFil), mas a **arquitetura é multiusuário desde o primeiro dia**.

**Stack:** Python 3.12 · Django 4.2+ · PostgreSQL · Bootstrap 5 · HTMX · Docker · Pytest · Deploy no Render.

---

## Glossário rápido

| Termo | Significado |
|---|---|
| **Disciplina (Subject)** | Matéria. Ex.: Português, Saúde Única. Cada seção do banco mestre é uma disciplina. |
| **Tópico (Topic)** | Subdivisão de uma disciplina. Ex.: "Interpretação de Texto". |
| **Questão (Question)** | Pergunta com enunciado + 4 alternativas + 1 correta + comentário. |
| **Alternativa (Alternative)** | Opção A–D de uma questão. |
| **Quiz** | Sessão de resolução (treino ou simulado) montada para um usuário. |
| **Gabarito** | A letra correta de cada questão. |
| **Service Layer** | Camada de classes Python que concentra a regra de negócio, fora das views. |
| **Idempotência** | Propriedade de rodar uma operação várias vezes com o mesmo resultado (importar 2× não duplica). |
| **CBV / FBV** | Class-Based View / Function-Based View (Django). |

---

## Status das fases

| Fase | Tema | Status |
|---|---|---|
| 1 | Arquitetura | ✅ Concluída (design) |
| 2 | Modelagem | ✅ Concluída (design) |
| 3 | Importador das 800 questões | ✅ Concluída (implementada e validada) |
| 4 | Autenticação | ✅ Concluída (implementada e validada) |
| 5 | Banco de questões (resolução) | ✅ Concluída (implementada e validada) |
| 6 | Dashboard | ✅ Concluída (implementada e validada) |
| 7 | Estatísticas e pontos fracos | ✅ Concluída (implementada e validada) |
| 8 | Simulados | ✅ Concluída (implementada e validada) |
| 9 | Qualidade | ⬜ Pendente |
| 10 | Deploy | ⬜ Pendente |

---
---

# FASE 1 — Arquitetura

## Objetivo

Definir **toda a arquitetura antes de escrever código**: estrutura de pastas, apps Django, camadas, fluxos, e as decisões de stack (linguagem, banco, frontend, infraestrutura). A meta é evitar retrabalho nas fases seguintes (estatísticas, simulados, importação).

## Problema que a fase resolve

Sem uma arquitetura definida, cada funcionalidade nova seria implementada de forma ad hoc, gerando:
- lógica de negócio espalhada dentro das views (difícil de testar),
- acoplamento entre módulos não-relacionados,
- decisões de infraestrutura tomadas tarde demais (e caras de reverter).

A Fase 1 estabelece **fronteiras claras** (apps) e uma **camada de serviços** que isola a regra de negócio.

## Arquivos criados

Nesta fase **nenhum código foi escrito** — o entregável é o **desenho**. Os artefatos são as decisões registradas (e agora consolidadas aqui). A estrutura física de pastas foi materializada parcialmente na Fase 3 (`apps/questions/...`).

## A arquitetura em camadas

O sistema é um **Monolito Modular** (Majestic Monolith). Camadas, de cima para baixo:

```
┌─────────────────────────────────────────────┐
│ Presentation — Django Templates + Bootstrap 5 │  ← o que o usuário vê
│                (+ HTMX para reatividade)      │
├─────────────────────────────────────────────┤
│ View Layer — Class-Based Views                │  ← recebe request, devolve response
├─────────────────────────────────────────────┤
│ Service Layer — classes Python com regra de   │  ← O CÉREBRO. Onde mora a regra.
│ negócio                                       │
├─────────────────────────────────────────────┤
│ Repository — QuerySets / Managers             │  ← consultas encapsuladas
├─────────────────────────────────────────────┤
│ Data — Django ORM + PostgreSQL                │  ← persistência
├─────────────────────────────────────────────┤
│ Infra — Redis (cache) + Celery (tasks)        │  ← suporte (fase posterior)
└─────────────────────────────────────────────┘
```

**Princípio central:** a **View não pensa**. Ela coleta o input, chama um **Service**, e devolve a resposta. Toda a regra de negócio vive na Service Layer — que é Python puro e testável sem HTTP.

## Estrutura de pastas

```
nicia-track/
├── config/                  # Configuração do projeto Django
│   ├── settings/
│   │   ├── base.py          # comum a todos os ambientes
│   │   ├── development.py    # DEBUG ligado, conveniências locais
│   │   ├── production.py     # segurança, logging, static
│   │   └── testing.py        # banco de teste, mocks
│   ├── urls.py / wsgi.py / asgi.py
│
├── apps/                    # Apps de domínio (cada um uma fronteira)
│   ├── core/                # utilitários compartilhados
│   ├── accounts/            # autenticação e perfil
│   ├── questions/           # banco de questões  ← já implementado (Fase 3)
│   ├── exams/               # simulados e sessões
│   ├── performance/         # desempenho e analytics
│   └── dashboard/           # painel principal
│
├── services/                # Service Layer transversal
├── templates/               # templates globais + partials HTMX
├── static/                  # css / js / imagens
├── tests/                   # unit / integration / functional
├── docker/                  # Dockerfile + compose
├── requirements/            # base / development / production
├── docs/                    # esta documentação + banco mestre
└── manage.py
```

## Apps criados e suas responsabilidades

| App | Responsabilidade | Por que existe separado |
|---|---|---|
| **core** | `BaseModel` (UUID, timestamps, soft delete), mixins de view, validators, exceções de domínio | Evita repetição e dá um "tronco comum" a todos os apps |
| **accounts** | `User` (email como login) + `Profile`, telas de cadastro/login/perfil | Identidade é um domínio próprio; isolá-la facilita trocar a estratégia de auth |
| **questions** | `Subject`, `Topic`, `Question`, `Alternative`, filtros, importação | É o coração do conteúdo; precisa de fronteira clara para curadoria |
| **exams** | `Quiz`, `QuizQuestion`, `UserAnswer`, sessão (iniciar/pausar/finalizar) | Resolução e simulado têm regras de estado complexas |
| **performance** | `UserSubjectStat`, `StudySession`, agregações, pontos fracos | Analytics tem consultas pesadas; isolá-las evita poluir o app de questões |
| **dashboard** | Visão consolidada, widgets, agenda | Orquestra dados dos outros apps numa única tela |

## Fluxo geral do sistema

```
Usuário se cadastra/loga (accounts)
   → escolhe treinar (questions) ou fazer simulado (exams)
   → resolve questões; cada resposta é registrada (exams → UserAnswer)
   → ao finalizar, o desempenho é processado (performance)
   → o dashboard mostra a evolução consolidada (dashboard)
```

## Decisões arquiteturais

### Por que Monolito Modular (e não microsserviços)?
- **Escolhido:** escopo coeso, equipe pequena, domínio único. Apps dão modularidade sem a complexidade operacional de múltiplos serviços, deploys e redes.
- **Alternativa:** microsserviços. **Rejeitada** por excesso de complexidade (orquestração, latência de rede, observabilidade) sem ganho real neste escopo.
- **Vantagem:** simples de desenvolver, testar e implantar; refatorar fronteiras é barato.
- **Desvantagem:** escala como uma unidade só; mitigável muito além do tamanho deste projeto.

### Por que Service Layer?
- Mantém as views finas e a regra de negócio **testável sem HTTP**.
- **Alternativa:** lógica nas views ou nos models ("fat models"). **Rejeitada**: views viram difíceis de testar; models acumulam responsabilidades demais.

### Por que HTMX (e não React/Vue)?
- **Escolhido:** dá reatividade (responder questão sem recarregar a página) com complexidade mínima e mantendo a renderização no servidor.
- **Alternativa:** SPA (React/Vue). **Rejeitada**: exigiria API separada, build de frontend, e duplicação de lógica — desnecessário para o escopo.

### Por que Django?
- "Batteries included": ORM, auth, admin, migrations, forms, segurança (CSRF, XSS, SQL injection) prontos.
- Admin nativo é **ideal para a curadoria das 800 questões**.
- Ecossistema maduro de testes (pytest-django) e deploy.
- **Alternativa:** Flask/FastAPI. **Rejeitada**: exigiria montar manualmente auth, admin e ORM — reinventar o que o Django entrega pronto.

### Por que PostgreSQL?
- Banco relacional robusto, com integridade referencial (FKs, constraints), índices parciais, e tipos ricos.
- O domínio é **fortemente relacional** (questões↔alternativas↔respostas↔usuários) — encaixa perfeitamente.
- Suporte de primeira classe no Django e no Render (managed, com backup).
- **Alternativa:** MySQL (menos recursos: índices parciais, tipos) ou NoSQL (**rejeitado**: perderíamos integridade relacional, que é essencial aqui).

### Por que Bootstrap 5?
- Grid responsivo pronto → **mesma experiência em desktop e mobile** (requisito do projeto) sem escrever CSS de layout do zero.
- Componentes acessíveis e consistentes.
- **Alternativa:** Tailwind (mais flexível, porém mais verboso e com curva maior) ou CSS próprio (lento). Bootstrap entrega o requisito de responsividade com menos esforço.

### Por que Docker?
- **Paridade dev/produção:** "funciona na minha máquina" deixa de ser problema.
- Postgres + app sobem com um comando (`docker-compose up`).
- O Render consome a mesma imagem.

### Por que Render (deploy)?
- PaaS simples com **PostgreSQL gerenciado + backups**, deploy via git, e free tier generoso.
- Menos operação que AWS bruto; mais barato/simples que Heroku.
- **Alternativa:** Railway/Fly.io (equivalentes) ou AWS (poderoso, porém operacionalmente caro). Render equilibra simplicidade e custo.

## Vantagens da arquitetura escolhida

- Testável (regra isolada em services).
- Evolutiva (apps com fronteiras claras).
- Barata de operar (um monolito, um banco, um PaaS).
- Responsiva por padrão (Bootstrap + templates server-side).

## O que aprendi nesta fase

- **Monolito Modular vs microsserviços** — quando cada um faz sentido.
- **Service Layer** como padrão para isolar regra de negócio.
- **Server-side rendering + HTMX** como alternativa pragmática a SPAs.
- Critérios de escolha de stack baseados em **requisito do projeto**, não em moda.

## Perguntas de entrevista

**P1. Por que escolher um monolito em vez de microsserviços?**
R: Para um domínio coeso e equipe pequena, microsserviços adicionam complexidade (rede, orquestração, deploys múltiplos, observabilidade) sem ganho. O monolito modular dá separação lógica via apps e mantém a operação simples; as fronteiras podem ser extraídas para serviços depois, se necessário.

**P2. O que é uma Service Layer e qual problema ela resolve?**
R: É uma camada de classes Python que concentra a regra de negócio, fora das views e dos models. Resolve o acoplamento entre HTTP e domínio: a regra fica testável sem request, as views ficam finas, e os models não acumulam lógica demais.

**P3. Por que HTMX em vez de React?**
R: O sistema é renderizado no servidor. HTMX adiciona reatividade pontual (trocar fragmentos de HTML via requisição) sem precisar de uma SPA, API separada e build de frontend — menos complexidade para o mesmo resultado neste escopo.

**P4. Por que PostgreSQL e não um NoSQL?**
R: O domínio é fortemente relacional e exige integridade (uma resposta referencia uma alternativa que pertence a uma questão de um usuário). FKs, constraints e transações do Postgres garantem isso; um NoSQL exigiria reimplementar integridade na aplicação.

## Resumo executivo

A Fase 1 definiu um **monolito modular em Django** organizado em apps de domínio, com **Service Layer** isolando a regra de negócio, **templates Bootstrap + HTMX** para uma UI responsiva igual em desktop e mobile, **PostgreSQL** pela natureza relacional do domínio, e **Docker + Render** para paridade de ambiente e deploy simples. Todas as escolhas foram guiadas pelos requisitos (multiusuário, responsivo, testável) e não por tendência.

---
---

# FASE 2 — Modelagem

## Objetivo

Desenhar **todas as entidades** do banco de dados, seus relacionamentos, campos, índices, constraints e regras de negócio — antes de gerar migrations.

## Problema que a fase resolve

Um modelo mal pensado é o erro mais caro de corrigir: migrations de produção, dados a migrar, código a reescrever. A Fase 2 antecipa o domínio inteiro (questões, simulados, respostas, estatísticas, histórico) para que as fases seguintes apenas **consumam** um modelo estável.

## Arquivos criados

Design (sem código). As classes de model serão materializadas em `apps/*/models.py` no scaffolding do Django. A Fase 3 já **assume** este modelo e adiciona 3 campos (ver [Ajustes da Fase 3](#ajustes-de-modelo-introduzidos-pela-fase-3)).

## Diagrama de entidades (lógico)

```
User ──1:1── Profile
  │
  ├─1:N─ Quiz ──1:1── StudySession
  │        │
  │        ├─M:N─ Question   (via QuizQuestion)
  │        └─1:N─ UserAnswer ──N:1── Alternative
  │
  └─1:N─ UserSubjectStat ──N:1── Subject

Subject ─1:N─ Topic
Subject ─1:N─ Question ─1:N─ Alternative
Topic   ─1:N─ Question
```

## Models criados — detalhe por entidade

> Para cada model: **função**, **relacionamentos** e **impacto no sistema**.

### `User` (estende `AbstractUser`)
- **Função:** identidade e autenticação. Usa **email como login** (`USERNAME_FIELD = 'email'`, UNIQUE).
- **Relacionamentos:** 1:1 com `Profile`; 1:N com `Quiz`, `StudySession`, `UserAnswer`, `UserSubjectStat`.
- **Impacto:** raiz de tudo que é "por usuário". Estender `AbstractUser` (em vez de usar o User padrão) é decisão consciente: permite evoluir o modelo de usuário sem migration traumática depois.

### `Profile`
- **Função:** dados de estudo do usuário (concurso-alvo, meta diária, nível, bio, avatar).
- **Relacionamentos:** 1:1 com `User` (CASCADE).
- **Impacto:** separa "quem o usuário é" (auth) de "como ele estuda" (preferências), mantendo o `User` enxuto.

### `Subject` (Disciplina)
- **Função:** matéria. Ex.: Português, Saúde Única.
- **Relacionamentos:** 1:N com `Topic` e `Question`.
- **Impacto:** eixo de filtragem e de estatística. Ganhou na Fase 3 o campo **`category`** (basic/specific) para montar a distribuição do simulado.

### `Topic` (Tópico)
- **Função:** subdivisão da disciplina.
- **Relacionamentos:** N:1 com `Subject`; 1:N com `Question` (nullable na questão).
- **Impacto:** granularidade fina para identificar pontos fracos (Fase 7). Slug único **dentro** da disciplina.

### `Question`
- **Função:** a questão em si — enunciado, banca, ano, dificuldade, comentário.
- **Relacionamentos:** N:1 com `Subject` (PROTECT) e `Topic` (PROTECT, nullable); 1:N com `Alternative`.
- **Impacto:** entidade central de conteúdo. `is_active=False` esconde de novos quizzes mas **preserva o histórico**. Ganhou na Fase 3: `external_id`, `content_hash`, `context_text`.

### `Alternative`
- **Função:** opção A–D de uma questão, com flag `is_correct`.
- **Relacionamentos:** N:1 com `Question` (CASCADE).
- **Impacto:** **exatamente uma** correta por questão (regra de negócio). Letra única por questão.

### `Quiz`
- **Função:** uma sessão de resolução (treino ou simulado), com tipo, status, limite de tempo.
- **Relacionamentos:** N:1 com `User`; M:N com `Question` via `QuizQuestion`; 1:N com `UserAnswer`; 1:1 com `StudySession`.
- **Impacto:** carrega a **máquina de estados** (created → in_progress → finished/expired).

### `QuizQuestion` (tabela de junção)
- **Função:** liga `Quiz` ↔ `Question` com **ordem**.
- **Relacionamentos:** N:1 com `Quiz` (CASCADE) e `Question` (PROTECT).
- **Impacto:** permite controlar a ordem de exibição e impedir questão repetida no mesmo quiz (UNIQUE `(quiz, question)` e `(quiz, order)`).

### `UserAnswer`
- **Função:** a resposta do usuário a uma questão dentro de um quiz.
- **Relacionamentos:** N:1 com `Quiz` (CASCADE), `Question` (PROTECT), `Alternative` (nullable = pulou).
- **Impacto:** base de toda estatística. `is_correct` é **calculado e gravado no submit** (nunca recalculado depois). UNIQUE `(quiz, question)`.

### `StudySession`
- **Função:** resumo de uma sessão de estudo (data, totais, duração) — base de streak e metas diárias.
- **Relacionamentos:** N:1 com `User`; 1:1 com `Quiz`.
- **Impacto:** evita recomputar agregados a partir de milhares de `UserAnswer` para a tela de evolução.

### `UserSubjectStat` (agregação)
- **Função:** desempenho acumulado de um usuário por disciplina (total respondido, total correto).
- **Relacionamentos:** N:1 com `User` e `Subject`. UNIQUE `(user, subject)`.
- **Impacto:** acelera o dashboard e os pontos fracos via **upsert** após cada quiz, em vez de varrer todas as respostas. `accuracy_pct` é **derivado**, nunca armazenado.

## Índices (os mais importantes)

| Tabela | Índice | Para quê |
|---|---|---|
| Question | `(subject, topic, difficulty, is_active)` | Filtros da tela de resolução |
| Quiz | `(user, status)` / `(user, created_at desc)` | Listar quizzes do usuário |
| UserAnswer | UNIQUE `(quiz, question)` | Integridade + busca de respostas |
| StudySession | `(user, date desc)` | Streak e evolução |
| UserSubjectStat | UNIQUE `(user, subject)` | Upsert e dashboard |
| Alternative | parcial `(question) WHERE is_correct` | Achar a correta rápido |

## Constraints e regras de negócio

- **Email** único; usado como login.
- **Alternativa:** letra única por questão; **exatamente uma** `is_correct=True` por questão (validado na service layer).
- **Topic** deve pertencer ao mesmo `Subject` da questão.
- **Quiz** só inicia se estiver `created`; não aceita respostas se `finished`/`expired`; simulado tem exatamente 40 questões.
- **Resposta** só pode apontar para alternativa que pertence à questão; `is_correct` calculado no submit.
- **`accuracy_pct`** sempre derivado (`correct/answered*100`).
- **Streak** calculado dinamicamente a partir de `StudySession.date` (não armazenado); só conta o dia com ≥1 questão.
- **PROTECT vs CASCADE:** apagar um `User` apaga seus quizzes/respostas (CASCADE); mas uma `Question` não pode ser apagada se há respostas/quizzes apontando para ela (PROTECT) — preserva integridade do histórico.

## Decisões de modelagem

- **UUID como PK** (via `BaseModel`): IDs não sequenciais, seguros de expor em URLs, e fáceis de mesclar entre ambientes.
- **Agregados materializados** (`UserSubjectStat`, `StudySession`): trocam um pouco de redundância controlada por **performance de leitura** no dashboard. Atualizados por service, em transação.
- **Soft delete + `is_active`**: nada de conteúdo é destruído; questões saem de circulação preservando histórico.

### Ajustes de modelo introduzidos pela Fase 3

A análise dos dados reais exigiu 3 acréscimos (a aplicar no scaffolding):

| Model | Campo | Motivo |
|---|---|---|
| `Subject` | `category` (`basic` / `specific`) | Montar a distribuição do simulado (5+5+5+5+20) na Fase 8 |
| `Question` | `external_id` (slug, UNIQUE) | Identidade estável para reimportação idempotente |
| `Question` | `content_hash` (char 64) | Detectar edições e atualizar sem duplicar |
| `Question` | `context_text` (TextField, nullable) | Textos-base de Português exibidos uma vez por grupo |

## Vantagens e possíveis melhorias futuras

**Vantagens:** integridade forte, leituras rápidas (agregados + índices), histórico preservado, pronto para multiusuário.

**Melhorias futuras:**
- Tags livres em `Question` para classificação cruzada.
- Particionamento de `UserAnswer` se o volume explodir.
- Tabela de `Achievement`/gamificação.
- Versionamento de questão (auditar correções de conteúdo).

## O que aprendi nesta fase

- **Modelagem relacional** (1:1, 1:N, M:N com through table).
- **`on_delete`**: CASCADE vs PROTECT vs SET_NULL e suas consequências.
- **Desnormalização controlada** (agregados) para performance de leitura.
- **Índices parciais e compostos** alinhados às consultas reais.
- **Dado derivado vs armazenado** (`accuracy_pct`, streak).

## Perguntas de entrevista

**P1. Quando usar uma "through table" (tabela de junção explícita)?**
R: Quando o relacionamento M:N precisa de **atributos próprios**. Aqui, `QuizQuestion` guarda a `order` da questão no quiz — impossível com um M:N simples.

**P2. Por que `is_correct` é gravado na resposta em vez de calculado na hora de exibir?**
R: O gabarito de uma questão pode ser corrigido depois. Gravar o resultado no momento do submit **congela** o histórico: a estatística do usuário reflete o que era verdade quando ele respondeu, e não muda retroativamente.

**P3. Diferença entre CASCADE e PROTECT no `on_delete`?**
R: CASCADE apaga os filhos junto com o pai (apagar `User` apaga seus `Quiz`). PROTECT impede apagar o pai se houver filhos (não dá para apagar uma `Question` que tem respostas) — protege a integridade do histórico.

**P4. Por que materializar `UserSubjectStat` se dá para somar `UserAnswer`?**
R: Performance de leitura. O dashboard e os pontos fracos seriam `GROUP BY` sobre dezenas de milhares de respostas a cada acesso. O agregado é atualizado por **upsert** no fim de cada quiz e lido em O(1) por disciplina.

## Resumo executivo

A Fase 2 modelou 11 entidades cobrindo usuários, conteúdo (disciplina→tópico→questão→alternativa), resolução (quiz→junção→resposta) e analytics (sessão, estatística por disciplina). As decisões-chave: **UUID como PK**, **integridade forte** com PROTECT/CASCADE, **agregados materializados** para leitura rápida, e **dados derivados** (accuracy, streak) calculados sob demanda. O modelo é estável o suficiente para que as fases seguintes apenas o consumam.

---
---

# FASE 3 — Importador das Questões

## Objetivo

Transformar o arquivo **`docs/15_BANCO_MESTRE_DE_QUESTOES.md`** em **registros persistidos no PostgreSQL** — 800 questões com suas 3.200 alternativas, gabaritos e comentários, distribuídas em 13 disciplinas.

## Problema que a fase resolve

São **~800 questões**. Cadastrar manualmente uma a uma (cada qual com 4 alternativas, gabarito e comentário) seria **inviável** — dezenas de horas, propenso a erro. E sempre que o arquivo for corrigido, refazer o cadastro à mão seria pior ainda.

**Solução:** um **Management Command** que lê o markdown, faz parsing automático e persiste tudo — de forma **idempotente** (rodar de novo não duplica; corrigir o `.md` e reimportar propaga a correção).

## Estrutura do markdown (a fonte)

O arquivo é **altamente regular** — fato confirmado por análise antes de codar:

| Característica | Valor |
|---|---|
| Total de questões | **800** |
| Seções (disciplinas) | **13** |
| Alternativas por questão | **4** (A–D), nunca E |
| Gabaritos | 800, todos A–D, distribuídos **200/200/200/200** |
| Imagens | nenhuma |
| Questões anuladas | nenhuma |
| Numeração | **reinicia em 1** a cada seção |
| Textos-base | só em Português: **2** (Texto I: q1–5; Texto II: q51–54 → 9 questões) |

Formato de uma seção:

```
# SEÇÃO 1 — SAÚDE ÚNICA
### 50 questões | Base: `01_SAUDE_UNICA_MASTER.md`

**1.** Sobre o conceito de Saúde Única, assinale a correta.
A) ...
B) ...
C) ...
D) É uma abordagem integrada e unificada...

---

### 🔑 GABARITO E COMENTÁRIOS — SEÇÃO 1
| Q | Gab | Comentário resumido | Ref. MASTER |
|---|-----|---------------------|-------------|
| 1 | **D** | Definição OHHLEP... | 01 §3.1 |

---
---
```

Em Português há ainda o bloco de texto-base:
```
> Texto I para as questões 1 a 5:
>
> *"...texto..."*
```

## Arquivos criados

```
apps/questions/
├── importer/
│   ├── parser.py          ← parser em Python puro (sem Django)
│   └── mapping.py         ← 13 seções → disciplinas + categoria
├── services/
│   └── import_service.py  ← persistência idempotente (Django ORM)
└── management/commands/
    └── import_questions.py ← o comando manage.py
scripts/
└── validate_parse.py      ← validador standalone (roda sem Django)
tests/
├── unit/test_parser.py            ← 11 testes (inclui o arquivo real)
└── integration/test_import_service.py ← idempotência (roda com DB)
```

## Arquivos modificados

- `docs/PROJECT_EXPLAINED.md` — este documento.
- Modelo da Fase 2 — **ajustado** com `Subject.category`, `Question.external_id`, `Question.content_hash`, `Question.context_text` (ver Fase 2 → Ajustes).

## Classes criadas

> **Nota:** a implementação real separa **parsing** (uma classe) de **persistência** (outra). O exemplo do roadmap citava uma classe única `QuestionImporter`; optou-se por **duas responsabilidades distintas** para maximizar testabilidade.

### `BancoMestreParser` (`importer/parser.py`)
- **Responsabilidade:** converter o texto markdown em objetos `ParsedQuestion` — **sem tocar no banco nem importar Django**.
- **Por que foi criada?** Centralizar todo o parsing num lugar testável isoladamente. Por não depender de Django, **roda contra o arquivo real sem subir banco** (validação imediata).
- **Quando é utilizada?** Chamada pelo `QuestionImportService` (e pelo `validate_parse.py`).
- **Alternativa considerada:** fazer o parsing dentro do command. **Rejeitada:** acoplaria a lógica ao Django, dificultaria o teste e misturaria I/O de terminal com regra de parsing.

### `ParsedQuestion`, `ParsedAlternative` (dataclasses)
- **Responsabilidade:** representar uma questão/alternativa extraída, **antes** de virar model.
- **Por que existem?** Desacoplam o resultado do parser do ORM. `ParsedQuestion` calcula dois valores-chave:
  - **`external_id`** = `banco-mestre-s{seção:02d}-q{número:03d}` → identidade estável.
  - **`content_hash`** = SHA-256 do conteúdo normalizado → detecta edições.
- **Quando são usadas?** Saída do parser, entrada do service.

### `ParseResult` e `ParseError`
- **Responsabilidade:** `ParseResult` agrega todas as questões + todos os erros + estatísticas; `ParseError` descreve um problema (seção, número, mensagem).
- **Por que existem?** Permitem **coletar todos os erros de uma vez** (em vez de estourar no primeiro), dando panorama completo numa rodada.

### `SubjectMapping` / `SUBJECT_MAP` (`importer/mapping.py`)
- **Responsabilidade:** mapear cada uma das 13 seções para uma disciplina (nome, slug, **categoria** basic/specific, cor).
- **Por que foi criada?** O `category` é o que vai permitir a distribuição do simulado na Fase 8 (5 básicas + 20 específicas). Centralizar o mapeamento evita "magic strings" espalhadas.

### `QuestionImportService` (`services/import_service.py`)
- **Responsabilidade:** orquestrar parse + **persistência idempotente** no banco.
- **Por que foi criada?** É a Service Layer da Fase 1 aplicada: o command não fala com o ORM, o parser não fala com o ORM — só o service.
- **Quando é utilizada?** Chamada pelo command (`import_questions`).

### `ImportReport`
- **Responsabilidade:** resultado da importação (criadas, atualizadas, inalteradas, disciplinas, erros).
- **Por que existe?** Dá uma saída estruturada e testável (sem depender de print).

### `Command` (`management/commands/import_questions.py`)
- **Responsabilidade:** interface de linha de comando — argumentos, I/O de terminal, exit codes.
- **Por que foi criada?** É o ponto de entrada operacional. Só faz I/O; delega 100% da lógica ao service.

## Services criados

### `QuestionImportService`
- **Responsabilidade:** transformar `ParseResult` em registros no Postgres, sem duplicar.
- **Fluxo:**
  1. `import_from_file(path)` → chama o parser.
  2. Se o parse tem **qualquer** erro → retorna o relatório e **não grava nada** (fail-fast).
  3. `--dry-run`? → simula (conta create/update/unchanged comparando hashes) sem gravar.
  4. `_ensure_subjects()` → upsert das 13 disciplinas (`update_or_create` por slug).
  5. Para cada questão → `_upsert_question()` numa **transação atômica**:
     - `external_id` não existe → **CREATE** questão + `bulk_create` das 4 alternativas.
     - `content_hash` igual → **UNCHANGED** (pula).
     - `content_hash` diferente → **UPDATE** questão + apaga e regrava alternativas.
- **Motivo da criação:** isolar persistência e idempotência num único lugar testável.

## Models criados

A Fase 3 **não cria models novos** — ela **popula** os models da Fase 2 (`Subject`, `Question`, `Alternative`) e exige os 3 campos adicionais já citados. Esse é o "contrato" entre as fases: o importador depende de `apps.questions.models`.

## Fluxo de execução (passo a passo)

Como as **800 questões saem do markdown e chegam ao PostgreSQL**:

```
1.  Operador roda:  python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md
2.  Command valida que o arquivo existe e instancia QuestionImportService.
3.  Service chama BancoMestreParser.parse_file(path).
4.  Parser lê o arquivo e QUEBRA por "# SEÇÃO N"  → 13 blocos.
5.  Para cada bloco:
      a. Extrai número e título da seção (regex).
      b. Extrai o arquivo-base do subtítulo "### N questões | Base: `...`".
      c. Separa CORPO (questões) do GABARITO (split em "### 🔑 GABARITO").
      d. No corpo, captura textos-base ("> Texto I para as questões 1 a 5:").
      e. Lê cada "**N.**" como início de questão; acumula o enunciado.
      f. Lê "A) … B) … C) … D)" como alternativas.
      g. No gabarito, lê cada linha "| N | **X** | comentário | ref |".
      h. MERGE: casa a questão N com a linha N do gabarito →
         marca a alternativa X como correta, anexa comentário e ref;
         se a questão está no range de um texto-base, anexa o context_text.
      i. VALIDA cada questão (4 alternativas A–D, exatamente 1 correta,
         gabarito presente, sem enunciado/alternativa vazios).
6.  Parser devolve ParseResult (800 questões, lista de erros).
7.  Service: se houver QUALQUER erro → relata e ABORTA (nada gravado).
8.  Service faz upsert das 13 disciplinas (Subject) com category basic/specific.
9.  Para cada questão (transação atômica):
      - calcula external_id e content_hash;
      - decide CREATE / UNCHANGED / UPDATE comparando o hash com o banco;
      - grava a Question e bulk_create das 4 Alternatives.
10. Service devolve ImportReport; o command imprime
    criadas / atualizadas / inalteradas / disciplinas.
```

**Evidência real de execução** (via `scripts/validate_parse.py` contra o arquivo verdadeiro):
```
Total de questoes : 800   |   Total de secoes : 13   |   Total de erros : 0
Distribuicao de gabaritos: {'A': 200, 'B': 200, 'C': 200, 'D': 200}
Questoes com texto-base (contexto): 9
11 passed in 0.08s   (testes do parser)
```

## Validações

**No parser (por questão):** exatamente 4 alternativas na ordem A,B,C,D; enunciado e alternativas não vazios; gabarito presente e em A–D; exatamente 1 correta; detecção de gabarito órfão (sem questão) e questão sem gabarito.

**No service:** fail-fast (qualquer erro de parse aborta a gravação inteira); transação atômica por questão (questão + alternativas nunca ficam pela metade).

## Tratamento de erros

- **Coleta, não interrompe:** o parser acumula **todos** os erros (com seção + número) em `ParseResult.errors`, dando o panorama completo numa única rodada.
- **`--strict`:** o command sai com código ≠ 0 se houver erro (útil em CI).
- **`--dry-run`:** roda parse + validações e simula contra o banco, **sem gravar**.
- **Arquivo inexistente:** `CommandError` imediato.

## Prevenção de duplicidade (idempotência)

Estratégia de **dupla chave**:

| Chave | Função |
|---|---|
| **`external_id`** = `banco-mestre-s{seção}-q{número}` | Identidade estável (UNIQUE). Reimportar reusa o mesmo registro. |
| **`content_hash`** = SHA-256 do conteúdo normalizado | Detecta edição. Igual → pula (`unchanged`); diferente → atualiza (`updated`). |

- Rodar 2× → tudo `unchanged`, **zero duplicação**.
- Corrigir um comentário no `.md` e reimportar → aquela questão vira `updated`, com alternativas regravadas.
- **Trade-off:** `external_id` é **posicional**; inserir/reordenar questões no meio de uma seção remapearia os IDs. Para este arquivo (estável, append-only) é seguro. Fallback possível: dedup puramente por `content_hash`.

## Ganhos obtidos

- **Tempo:** ~800 questões cadastradas em segundos vs dezenas de horas manuais.
- **Confiabilidade:** validação automática garante 4 alternativas + 1 correta em todas.
- **Reprodutibilidade:** reimportar é seguro; correções no `.md` propagam.
- **Testabilidade:** parser puro testado contra o arquivo real (11 testes verdes).
- **Reuso futuro:** o mesmo importador serve para novos bancos no mesmo formato.

## O que aprendi nesta fase

- **Management Commands** (`BaseCommand`, `add_arguments`, `handle`, `CommandError`).
- **Parsing por máquina de estados** e **regex** para texto semiestruturado.
- **Idempotência** via chave natural + hash de conteúdo.
- **`bulk_create`** para inserir as alternativas em uma query por questão (menos round-trips ao banco).
- **`transaction.atomic`** para consistência (questão + alternativas como unidade).
- **`update_or_create`** para upsert de disciplinas.
- **Separar parsing de persistência** para testar cada um isoladamente.
- **`select_for_update`** para evitar corrida ao atualizar uma questão existente.

## Perguntas de entrevista

**P1. Por que usar `bulk_create`?**
R: Para inserir as 4 alternativas de uma questão em **uma única query** em vez de quatro. Reduz round-trips ao banco e melhora muito a performance ao escalar para milhares de inserts.

**P2. Como o importador evita duplicar questões ao rodar de novo?**
R: Cada questão tem um `external_id` estável (seção+número) com UNIQUE. Antes de criar, o service procura por esse id: se não existe, cria; se existe e o `content_hash` é igual, pula; se o hash mudou, atualiza. Assim a operação é **idempotente**.

**P3. Por que separar o parser do management command?**
R: Responsabilidade única e testabilidade. O parser é Python puro, sem Django — dá para testá-lo (e rodá-lo contra o arquivo real) sem subir banco. O command só cuida de I/O de terminal e delega ao service.

**P4. Por que `transaction.atomic` na persistência de cada questão?**
R: Para que questão e alternativas sejam gravadas como uma **unidade**. Se a inserção das alternativas falhasse no meio, a questão não pode ficar órfã (sem opções) — a transação garante tudo-ou-nada.

**P5. Por que o parser coleta todos os erros em vez de parar no primeiro?**
R: Para dar o panorama completo numa única rodada. Se há 5 questões malformadas, você quer ver as 5 de uma vez, corrigir o `.md` e reimportar — não descobrir uma por vez.

**P6. O que é idempotência e por que ela importa aqui?**
R: É a propriedade de uma operação produzir o mesmo resultado se executada várias vezes. Importa porque importações são repetidas (correções, novos lotes); sem idempotência, cada execução duplicaria dados.

## Resumo executivo

A Fase 3 implementou e **validou contra dados reais** um importador que leva as 800 questões do markdown ao PostgreSQL. A arquitetura separa **parser** (Python puro, testável isoladamente) de **service** (persistência idempotente via ORM), acionados por um **management command** com `--dry-run` e `--strict`. A idempotência usa **`external_id` + `content_hash`**, garantindo que reimportar não duplique e que correções propaguem. Resultado comprovado: 800 questões, 13 disciplinas, 0 erros de parsing, 11 testes verdes.

---
---

# FASE 4 — Autenticação

## Objetivo

Criar o módulo de identidade do sistema: cadastro de usuários, login por e-mail, logout com confirmação e edição de perfil. É a primeira fase com código Django real em execução — models, views CBV, services, templates Bootstrap 5 responsivos e testes pytest-django.

## Problema que a fase resolve

Sem autenticação, não há "por usuário" — nenhuma estatística, simulado ou progresso pode ser personalizado. Esta fase estabelece a **fundação de identidade** sobre a qual todo o resto do sistema será construído.

## Arquivos criados

```
config/
├── __init__.py
├── settings/
│   ├── __init__.py
│   ├── base.py          ← configuração base (todas as settings compartilhadas)
│   ├── development.py   ← SQLite, DEBUG=True
│   ├── testing.py       ← SQLite :memory:, MD5 hasher (testes rápidos)
│   └── production.py    ← PostgreSQL, HTTPS, segurança
├── urls.py              ← root URL dispatcher
└── wsgi.py

apps/core/
├── __init__.py
├── apps.py
├── models.py            ← BaseModel (UUID PK, timestamps)
└── exceptions.py        ← DomainException, ValidationError, NotFoundError

apps/accounts/
├── __init__.py
├── apps.py              ← AccountsConfig (registra signals no ready())
├── models.py            ← User (email login) + Profile + UserManager
├── forms.py             ← RegisterForm, LoginForm, ProfileForm
├── signals.py           ← post_save cria Profile automaticamente
├── views.py             ← RegisterView, LoginView, LogoutView, ProfileView
├── urls.py              ← /conta/ namespace="accounts"
└── services/
    └── user_service.py  ← UserService.register() / update_profile()

apps/questions/
├── apps.py
└── models.py            ← Subject, Topic, Question, Alternative

templates/
├── base.html            ← layout global com navbar e messages
└── accounts/
    ├── base_auth.html   ← layout de tela de autenticação (card centrado)
    ├── register.html
    ├── login.html
    ├── logout_confirm.html
    └── profile.html

tests/
├── conftest.py          ← fixtures: user, client_logged
├── unit/test_user_service.py
└── integration/test_auth_views.py

requirements/
├── base.txt             ← Django 4.2, psycopg2, decouple, Pillow, whitenoise
├── development.txt      ← + pytest, factory-boy, faker, black, isort
└── production.txt       ← + sentry-sdk

manage.py
pytest.ini
.env / .env.example
```

## Arquivos modificados

- `config/settings/base.py` — adicionado `STORAGES` para suporte ao WhiteNoise sem warning de deprecação.
- `apps/accounts/migrations/` — geradas `0001_initial.py` e `0002_alter_user_managers.py` (após criar o `UserManager` customizado).

## Models criados

### `User` (estende `AbstractUser`)
- **Função:** identidade do usuário. Email como campo de login (`USERNAME_FIELD = "email"`).
- **Por que estende `AbstractUser`?** Herda gratuitamente: hash de senha, `is_active`, `is_staff`, `date_joined`, `last_login`, grupos e permissões. Evita reescrever auth do zero.
- **`REQUIRED_FIELDS = []`** — sem campos obrigatórios além do email para `createsuperuser`.
- **`UserManager`** customizado: `create_user(email, password)` preenche `username` com o próprio email, tornando o campo `username` transparente para o sistema.
- **`display_name`** (property): retorna `first_name last_name` ou o prefixo do email — usado na navbar.
- **Relacionamentos:** 1:1 com `Profile`; raiz de tudo que é "por usuário".
- **Impacto:** `AUTH_USER_MODEL = "accounts.User"` em `base.py` — todas as FKs do sistema apontam para este model.

### `Profile`
- **Função:** dados de estudo separados da identidade (concurso-alvo, meta diária, nível, bio, avatar).
- **Por que separado do `User`?** Mantém o `User` focado em auth; `Profile` pode evoluir sem mexer na autenticação.
- **Criado automaticamente** via signal `post_save` — nunca fica órfão.
- **Relacionamentos:** `OneToOneField(User, CASCADE)` com `related_name="profile"` → acesso via `user.profile`.

### `BaseModel` (`apps.core`)
- **Função:** classe-pai abstrata com `id` (UUID4), `created_at` e `updated_at`.
- **Por que UUID?** IDs não sequenciais e seguros de expor em URLs; facilitam merge entre ambientes.
- **`abstract = True`** — não cria tabela própria; cada filho herda os campos.

## Services criados

### `UserService`
- **Responsabilidade:** toda a regra de negócio de usuário (registro e atualização de perfil).
- **Por que existe?** Views não podem manipular models diretamente — a Service Layer garante que a lógica seja testável sem HTTP e reutilizável.

**`UserService.register(form, request)`**
- Pega o form já validado.
- Cria o `User` sem salvar (`commit=False`), define `username = email`, chama `set_password()` (hash seguro), salva.
- O signal `post_save` cria o `Profile` automaticamente.
- Chama `login(request, user)` → sessão iniciada imediatamente após o cadastro.
- Envolto em `@transaction.atomic` — se qualquer passo falhar, nada é gravado.

**`UserService.update_profile(user, form)`**
- Salva as alterações do `Profile`.
- Atualiza `first_name`/`last_name` no `User` via `update_fields` (query mínima).
- Envolto em `@transaction.atomic`.

## Views criadas

Todas usam **Class-Based Views (CBV)** conforme arquitetura da Fase 1.

| View | Tipo base | URL | O que faz |
|---|---|---|---|
| `RegisterView` | `FormView` | `/conta/cadastro/` | Exibe e processa o formulário de cadastro |
| `LoginView` | `DjangoLoginView` | `/conta/login/` | Login por email/senha |
| `LogoutView` | `LoginRequiredMixin + TemplateView` | `/conta/logout/` | GET mostra confirmação; POST desloga |
| `ProfileView` | `LoginRequiredMixin + FormView` | `/conta/perfil/` | Exibe e salva edição de perfil |

**Por que CBV?**
- Reutilização via herança (ex.: `LoginView` herda do `DjangoLoginView` do Django, ganhando proteção CSRF e rate limiting gratuitamente).
- Separação de GET/POST estruturada (`get`, `form_valid`, `form_invalid`).
- `LoginRequiredMixin` aplicado como herança — não repete `@login_required` em todo método.

**`redirect_authenticated_user = True`** no `LoginView` → usuário logado que acessa `/login/` é redirecionado automaticamente, sem exibir o form.

## Templates criados

### `base.html`
- Layout global com navbar Bootstrap 5 (visível só para usuários logados).
- Renderiza o bloco de `{% if messages %}` — feedback de ações (sucesso, erro, info).
- Navbar responsiva com `navbar-toggler` → funciona em mobile.
- Botão "Sair" é um `<form method="post">` com CSRF — logout nunca via GET (segurança).

### `base_auth.html`
- Layout minimalista para telas de autenticação: card branco centralizado na tela.
- Herda de `base.html`? **Não** — deliberadamente não usa a navbar, pois o usuário ainda não está logado.
- Exibe logo, título e o block `{% card_content %}`.

### Padrão de exibição de erros nos templates
- Cada campo exibe `{{ form.campo.errors.0 }}` com classe `invalid-feedback d-block` — sem JavaScript, funciona com validação server-side pura.
- `{% if form.non_field_errors %}` captura erros que não pertencem a um campo específico (ex.: "As senhas não coincidem").

## Testes criados

**`tests/unit/test_user_service.py`** — 5 testes

| Teste | O que valida |
|---|---|
| `test_cria_usuario_com_email_como_username` | email vira username; senha faz hash |
| `test_cria_profile_automaticamente` | signal funciona; `user.profile` existe |
| `test_email_duplicado_invalida_form` | clean_email detecta duplicata |
| `test_senhas_diferentes_invalida_form` | clean() detecta mismatch |
| `test_atualiza_perfil` | salva profile + first_name/last_name |

**`tests/integration/test_auth_views.py`** — 13 testes

Cobrem: GET/POST de cada view, redirecionamento de usuário já logado, credenciais inválidas, proteção `LoginRequired`, e persistência real no banco.

**Resultado:** `18 passed` em 0.31s.

## Fluxo completo — como os dados percorrem o sistema

### Cadastro
```
1. Usuário acessa /conta/cadastro/  →  RegisterView.get()
2. Django renderiza register.html com RegisterForm vazio
3. Usuário preenche e submete
4. RegisterView.post() → form.is_valid()
     ├── clean_email(): verifica duplicata
     └── clean(): verifica senhas iguais
5. form_valid() → UserService.register(form, request)
     ├── User criado com set_password() (PBKDF2 + salt)
     ├── signal post_save → Profile criado automaticamente
     └── login(request, user) → sessão iniciada
6. Redirect para /conta/perfil/ com mensagem de sucesso
```

### Login
```
1. Usuário acessa /conta/login/  →  LoginView (herda DjangoLoginView)
2. POST com email + senha
3. Django autentica via UserManager (busca por email)
4. Sessão criada; redirect para /conta/perfil/
```

### Edição de Perfil
```
1. Usuário acessa /conta/perfil/  (requer login)
2. ProfileView.get() → form com instance=user.profile + initial do User
3. POST → form_valid() → UserService.update_profile(user, form)
     ├── profile.save()
     └── user.save(update_fields=["first_name", "last_name"])
4. Redirect para /conta/perfil/ com mensagem de sucesso
```

## Decisões arquiteturais

### Por que `email` como `USERNAME_FIELD` e não `username`?
O sistema é monodomínio (preparação para um concurso específico); o email é o identificador natural do usuário, não requer escolha de username e evita colisões. É mais amigável e segue o padrão de produtos modernos.

### Por que criar `UserManager` customizado?
O `BaseUserManager` do Django não sabe que nosso `USERNAME_FIELD = "email"`. Sem o manager customizado, `create_user()` exige `username` como 1º argumento — o que geraria confusão. O manager customizado encapsula essa lógica e torna `create_user(email, password)` a API natural.

### Por que `signal post_save` para criar o `Profile`?
Garante que **toda** criação de `User` — seja pelo cadastro, pelo admin, por fixtures de teste ou por scripts — gere um `Profile` automaticamente. A alternativa (criar no service) só funcionaria para o fluxo normal de cadastro, deixando outros pontos de criação vulneráveis à ausência de perfil.

**Alternativa considerada:** `get_or_create` nas views. **Rejeitada:** cada view precisaria verificar a existência do profile — código repetido e frágil.

### Por que `LogoutView` via POST e não GET?
Logout via GET é uma vulnerabilidade de segurança (CSRF logout attack): um link em qualquer site poderia deslogar o usuário. POST exige token CSRF — apenas o próprio sistema pode deslogar o usuário.

### Por que `LoginRequiredMixin` via herança (CBV) e não `@login_required` (FBV)?
Em CBV, `@login_required` precisaria ser aplicado no `dispatch` manualmente ou via decorador de classe (`method_decorator`). Herdar `LoginRequiredMixin` é mais limpo, explícito no nível da classe e funciona com todas as views que herdam dela.

### Por que `base_auth.html` separado do `base.html`?
Telas de autenticação não têm navbar (o usuário ainda não está logado). Um template separado evita herdar estrutura desnecessária e simplifica o layout centrado. É o padrão de produtos como GitHub, Notion e Linear.

## Explicação educacional

Imagine que você é um desenvolvedor júnior e nunca viu este código.

**O `User` estende `AbstractUser`** porque o Django já tem tudo que precisamos — hash de senha, sessões, permissões — e só queremos mudar o campo de login para email. É como herdar de uma classe e sobrescrever apenas o que precisa mudar.

**O `Profile` existe separado** porque misturar "quem você é" (email, senha) com "como você estuda" (concurso-alvo, meta diária) num modelo só violaria o princípio de responsabilidade única — e tornaria difícil evoluir um sem mexer no outro.

**O `UserService` existe** porque a view não deve saber como criar um usuário. A view só sabe que "o formulário foi válido, chama o service". O service sabe "preciso criar o user, fazer hash da senha, criar a sessão". Assim cada parte tem uma responsabilidade clara.

**O signal `post_save`** é como um gatilho automático: toda vez que um `User` é salvo pela primeira vez (`created=True`), o Django dispara esse sinal, e o handler cria o `Profile`. O desenvolvedor que usa o sistema não precisa lembrar de criar o perfil — acontece automaticamente.

**O `LoginRequiredMixin`** é como uma porta com crachá: qualquer view que o herda automaticamente exige que o usuário esteja logado. Se não estiver, é redirecionado para `/conta/login/` antes mesmo de a view rodar.

## Perguntas de entrevista

**P1. Por que usar CBV em vez de FBV nesta fase?**
R: CBV permite herança — `RegisterView(FormView)` ganha `form_valid`, `form_invalid` e `get_form_kwargs` prontos. `LoginView(DjangoLoginView)` herda proteção CSRF e autenticação já implementadas. A mesma lógica em FBV exigiria mais boilerplate. Para operações CRUD padronizadas, CBV é mais expressivo.

**P2. O que é `USERNAME_FIELD` no Django e por que mudamos para email?**
R: É o campo usado para identificação no login (`authenticate(request, username=..., password=...)`). Por padrão é `"username"`. Mudando para `"email"`, o Django usa email como identificador em todo o sistema de auth — AuthenticationForm, `authenticate()`, `createsuperuser`. É mais natural para usuários finais.

**P3. Por que `transaction.atomic` nos métodos do service?**
R: Garante atomicidade. Em `register`, o User é criado e a sessão é iniciada — se o login falhasse, o User não deveria ter sido criado. O `@transaction.atomic` envolve tudo numa única transação de banco: sucesso total ou rollback total.

**P4. O que é o `post_save` signal e quando ele executa?**
R: É um sinal que o Django dispara depois de qualquer chamada ao `save()` de um model. O `created` boolean indica se foi criação (True) ou atualização (False). Usamos para criar o `Profile` toda vez que um `User` novo é salvo — independentemente de onde o User foi criado.

**P5. Por que o `LoginView` usa `redirect_authenticated_user = True`?**
R: UX e segurança. Um usuário já logado não deve ver o formulário de login — seria confuso. Essa flag faz o Django redirecionar automaticamente para `LOGIN_REDIRECT_URL` se o usuário já estiver autenticado.

**P6. Como funciona a hierarquia `base.html` → `base_auth.html` → `login.html`?**
R: É herança de templates Django. `login.html` estende `base_auth.html` que tem o card centralizado. `base_auth.html` não estende `base.html` — é um layout completamente independente para as telas de autenticação. Cada nível sobrescreve blocos (`{% block card_content %}`).

**P7. Por que o `UserManager` foi necessário?**
R: Ao mudar `USERNAME_FIELD = "email"`, a assinatura esperada de `create_user()` muda, mas o `BaseUserManager` não sabe disso — ele ainda espera o campo padrão `username` como primeiro argumento. O `UserManager` customizado define `create_user(email, password)` explicitamente e preenche `username` automaticamente com o email.

## O que aprendi nesta fase

**Django:**
- `AbstractUser` vs `AbstractBaseUser` — quando usar cada um.
- `USERNAME_FIELD` e `REQUIRED_FIELDS` para customizar o modelo de usuário.
- `BaseUserManager` e como criar um manager customizado.
- Signals Django (`post_save`, `@receiver`) e o papel do `apps.py.ready()`.
- `LoginRequiredMixin` em CBV.
- `AuthenticationForm` e como o `LoginView` do Django funciona internamente.
- Herança de templates (`{% extends %}`), `{% block %}` e layouts reutilizáveis.
- `messages` framework para feedback pós-redirect.
- `update_fields` em `save()` para queries mínimas.

**PostgreSQL / banco:**
- UUID como PK via `models.UUIDField(default=uuid4, editable=False)`.
- `OneToOneField` com `CASCADE` — apagar User apaga Profile junto.
- `unique=True` em `email` — constraint de banco que garante unicidade.
- Migrations: `makemigrations` gera arquivos de migração; `migrate` aplica ao banco.

**Python:**
- Decoradores de método vs herança de mixin.
- `commit=False` em forms para instanciar o objeto sem gravar.
- `@transaction.atomic` como context manager ou decorador.

**Arquitetura:**
- Separação View → Service → Model.
- Service Layer como camada testável sem HTTP.
- Signal como mecanismo de desacoplamento (Profile não sabe quem o criou).
- Por que logout por POST protege contra CSRF.

**Testes:**
- `pytest.mark.django_db` para acesso ao banco em testes.
- `client.force_login(user)` para simular usuário autenticado sem passar por views de login.
- Fixtures do pytest (`@pytest.fixture`) e sua reutilização entre testes.
- Testar redirecionamentos: `assert r.status_code == 302` + `r.url`.
- `MagicMock()` para simular o `request` em testes unitários de service.

## Resumo executivo

A Fase 4 scaffoldou o projeto Django completo (settings por ambiente, URLs, apps, Docker-ready) e implementou o módulo de autenticação: **User com email como login**, **Profile criado automaticamente via signal**, **4 views CBV** (cadastro, login, logout com confirmação, perfil), **UserService** isolando a regra de negócio, **5 templates Bootstrap 5 responsivos** e **18 testes (5 unitários + 13 integração) passando em 0.31s**. A decisão-chave foi o `UserManager` customizado para tornar `email` o identificador natural do sistema sem perder as conveniências do `AbstractUser`.

---

> **Próxima fase:** Fase 5 — Banco de Questões.

---
---

# FASE 5 — Banco de Questões

## Objetivo

Permitir que o usuário **resolva questões por disciplina, tópico e quantidade**, receba o gabarito comentado ao finalizar e veja seu resultado com acertos, erros e percentual.

## Problema que a fase resolve

O banco com 800 questões está no PostgreSQL (Fase 3), mas é inacessível ao usuário. Esta fase cria o fluxo completo de **treino**: filtrar → resolver → ver resultado. É o núcleo funcional do produto.

## Arquivos criados

```
apps/exams/
├── __init__.py
├── apps.py
├── models.py         ← Quiz, QuizQuestion, UserAnswer
├── forms.py          ← QuizFilterForm
├── views.py          ← FilterView, PlayQuizView, ResultView
├── urls.py           ← /questoes/ namespace="exams"
├── migrations/
│   └── 0001_initial.py
└── services/
    ├── __init__.py
    └── quiz_service.py   ← QuizService + QuizResult

apps/questions/services/
└── question_service.py   ← QuestionService

templates/exams/
├── filter.html       ← formulário de filtro
├── play.html         ← resolução das questões
└── result.html       ← gabarito comentado

tests/unit/test_quiz_service.py          ← 10 testes
tests/integration/test_exam_views.py     ← 11 testes
```

## Arquivos modificados

- `config/settings/base.py` — `apps.exams` adicionado a `INSTALLED_APPS`.
- `config/urls.py` — `path("questoes/", ...)` adicionado.

## Models criados

### `Quiz`
- **Função:** representa uma sessão de resolução — treino ou simulado — criada para um usuário.
- **Por que existe?** Agrupa as questões sorteadas e rastreia o estado (`in_progress` → `finished`). Sem ele, não há como saber quais questões o usuário deve responder nem se já terminou.
- **Campos-chave:** `user` (FK), `subject` (FK, nullable), `topic` (FK, nullable), `quiz_type` (`practice`/`simulated`), `status` (`in_progress`/`finished`), `quantity`, `started_at`, `finished_at`.
- **Relacionamentos:** `user` → N:1 com `User`; `subject`/`topic` → N:1 com as entidades de conteúdo; 1:N com `QuizQuestion` e `UserAnswer`.
- **Impacto:** ponto de entrada para a Fase 8 (Simulados) — o mesmo model suportará o modo `simulated` com distribuição de disciplinas.

### `QuizQuestion` (tabela de junção)
- **Função:** liga `Quiz` ↔ `Question` com **ordem** de exibição.
- **Por que não M:M direto?** Um M:M nativo no Django não carrega atributos extras. `QuizQuestion` guarda `order`, que define a sequência das questões no treino.
- **Constraints:** UNIQUE `(quiz, question)` — a mesma questão não aparece duas vezes; UNIQUE `(quiz, order)` — sem buracos ou duplicatas de ordem.
- **Relacionamentos:** N:1 com `Quiz` (CASCADE) e `Question` (PROTECT).

### `UserAnswer`
- **Função:** registra a resposta do usuário a cada questão dentro de um quiz.
- **`is_correct`** é calculado e **persistido no momento do submit** — não recalculado depois. Se o gabarito mudar no futuro, o histórico do usuário permanece fiel ao que era verdade quando ele respondeu.
- **`selected_alternative = None`** = questão pulada → conta como errada.
- **Constraint:** UNIQUE `(quiz, question)` — responde cada questão apenas uma vez por quiz.

## Services criados

### `QuestionService` (`apps/questions/services/question_service.py`)
- **Responsabilidade:** consultas ao banco de questões — filtrar, contar, sortear.
- **Fluxo de `get_practice_questions`:**
  1. Filtra `Question.objects` por `subject_id` e `is_active=True`.
  2. Se `topic_id` fornecido, adiciona filtro por tópico.
  3. `.order_by("?")` → ordem aleatória (PostgreSQL usa `ORDER BY RANDOM()`).
  4. `[:quantity]` → slicing limita ao número pedido.
  5. Retorna QuerySet com `prefetch_related("alternatives")`.
- **Por que separado do `QuizService`?** Responsabilidade única: `QuestionService` só sabe buscar questões; `QuizService` sabe criar e gerenciar quizzes.

### `QuizService` (`apps/exams/services/quiz_service.py`)
- **Responsabilidade:** criar quizzes, receber respostas e calcular resultados.

**`create_practice_quiz(user, subject_id, topic_id, quantity)`**
1. Busca questões via `QuestionService.get_practice_questions()`.
2. Cria `Quiz` com status `in_progress`.
3. `bulk_create` dos `QuizQuestion` com ordem sequencial.
4. Retorna o `Quiz` criado.
5. Tudo em `@transaction.atomic`.

**`submit_answers(quiz, raw_answers)`**
1. Verifica se o quiz já está `finished` → pula se sim (idempotência).
2. Para cada `QuizQuestion`, busca a alternativa selecionada no dict `raw_answers`.
3. Valida que a alternativa pertence à questão (segurança).
4. Calcula `is_correct` via `alternative.is_correct`.
5. `bulk_create` de todos os `UserAnswer`.
6. Marca `quiz.finished_at` e `quiz.status = finished`.
7. Tudo em `@transaction.atomic`.

**`get_result(quiz)`**
1. Busca `QuizQuestion` ordenado por `order` com `select_related` e `prefetch_related`.
2. Busca todos os `UserAnswer` do quiz num dict `{question_id: UserAnswer}`.
3. Monta lista `items` com: questão, alternativas, resposta selecionada, `is_correct`, `is_skipped`.
4. Calcula totais e percentual.
5. Retorna `QuizResult` dataclass.

### `QuizResult` (dataclass)
- **Função:** objeto de transferência do resultado — `total`, `correct`, `wrong`, `skipped`, `percentage`, `items`.
- **Por que dataclass?** Imutável, tipado, sem dependência de ORM — fácil de serializar e testar.

## Views criadas

| View | Tipo base | URL | O que faz |
|---|---|---|---|
| `FilterView` | `LoginRequiredMixin + FormView` | `GET/POST /questoes/` | Mostra filtros; no POST cria o quiz e redireciona |
| `PlayQuizView` | `LoginRequiredMixin + TemplateView` | `GET/POST /questoes/treino/<uuid>/` | GET exibe questões; POST submete respostas |
| `ResultView` | `LoginRequiredMixin + TemplateView` | `GET /questoes/resultado/<uuid>/` | Exibe gabarito comentado |

**Segurança:** `_get_quiz_for_user(quiz_id, user)` verifica que o quiz pertence ao usuário logado — retorna 404 se outro usuário tentar acessar.

**Tratamento de estado:** quiz `finished` em `PlayQuizView` → redirect automático para resultado; quiz `in_progress` em `ResultView` → redirect automático para play.

## Templates criados

### `filter.html`
- Card Bootstrap com `<select>` de disciplinas (populado do banco), `<select>` de tópicos e `<input type="radio">` para quantidade.
- **JavaScript mínimo** (inline): filtra as opções do select de tópicos conforme a disciplina selecionada, usando `data-subject` nos `<option>`. Zero dependências externas.

### `play.html`
- Exibe **todas as questões em página única** (como uma prova em papel).
- Cada questão: badge com número, texto e `<input type="radio" name="q_{question_id}" value="{alternative_id}">`.
- Texto-base de Português exibido em alerta acima da questão se `context_text` presente.
- Botão "Finalizar" com `confirm()` para evitar submit acidental.
- Navegação rápida por número de questão (âncoras) — útil no mobile.

### `result.html`
- Card de resumo: ícone de troféu/smile/frown por faixa de percentual, barra de progresso colorida, badges de acertos/erros/puladas.
- Lista de questões: verde (acerto), vermelho (erro), cinza (pulada).
- Para cada questão: alternativas com ícone ✓ (correta) / ✗ (selecionada e errada) / ○ (demais).
- Bloco de explicação (`question.explanation`) ao final de cada questão.

## Fluxo completo

```
1. Usuário acessa /questoes/                    → FilterView.get()
2. Escolhe Disciplina, Tópico (opt.), Quantidade → FilterView.post()
3. QuizService.create_practice_quiz()
   ├── QuestionService.get_practice_questions()  → ORDER BY RANDOM() LIMIT N
   ├── Quiz criado (status=in_progress)
   └── bulk_create QuizQuestion (com ordem)
4. Redirect para /questoes/treino/<uuid>/       → PlayQuizView.get()
   └── Exibe N questões com radio buttons
5. Usuário responde e clica "Finalizar"          → PlayQuizView.post()
   └── QuizService.submit_answers()
       ├── Para cada questão: verifica alt selecionada, calcula is_correct
       ├── bulk_create UserAnswer
       └── quiz.status = finished
6. Redirect para /questoes/resultado/<uuid>/    → ResultView.get()
   └── QuizService.get_result()
       ├── 2 queries otimizadas (select_related + prefetch_related)
       └── Monta QuizResult com items
7. Exibe resumo + gabarito comentado
```

## Decisões arquiteturais

### Por que exibir todas as questões em uma página em vez de uma por vez?
**Escolhido:** todas na mesma página (como uma prova de papel). Simples, sem JS complexo, sem estado de sessão, sem paginação. O usuário pode rolar, voltar e mudar respostas antes de finalizar.

**Alternativa:** uma questão por vez com HTMX (avança/volta sem reload). **Rejeitada para Fase 5** — adiciona complexidade de estado de progresso, é difícil de testar e não está previsto na Fase 8. Pode ser adicionado na Fase 9 (qualidade).

### Por que `ORDER BY RANDOM()` e não shuffle em Python?
`ORDER BY ?` (Django) → `ORDER BY RANDOM()` (PostgreSQL). O banco faz o sort antes de retornar as linhas — o slice `[:quantity]` já pega as N aleatórias. Em Python precisaríamos carregar todas e depois fazer `random.sample()`. O banco é mais eficiente para isso.

**Trade-off:** `ORDER BY RANDOM()` tem custo O(N) no banco. Para 800 questões é desprezível; para 800.000 questões seria revisto.

### Por que `bulk_create` para `QuizQuestion` e `UserAnswer`?
`QuizQuestion.objects.bulk_create([...])` faz **uma única query INSERT** independentemente de quantas questões. Sem `bulk_create`, seriam N queries (10, 20 ou 50 INSERTs). Para `UserAnswer` o ganho é idêntico.

### Por que `_get_quiz_for_user` helper em vez de `get_object_or_404(Quiz, pk=pk, user=user)`?
Ambos funcionam. O helper torna o código das views mais legível e centraliza a lógica de autorização num só lugar — se a regra mudar (ex.: admin pode ver qualquer quiz), muda em um ponto.

### Por que `QuizResult` como dataclass e não dict?
Tipagem, autocompletar, testabilidade. `result.correct` é mais legível que `result["correct"]`, e o dataclass valida os campos na criação.

## Explicação educacional

Imagine que você nunca viu este código.

**O `Quiz`** é como uma folha de prova gerada especificamente para você naquele momento. Ele registra quais questões você tem para responder e se você já terminou.

**O `QuizQuestion`** é a tabela de junção que diz "a questão X está na posição 3 dessa folha de prova". Sem ela, você saberia que a questão está na prova, mas não em qual ordem.

**O `UserAnswer`** é onde você escreve sua resposta na folha. Se deixou em branco, o campo `selected_alternative` fica `null`, o que conta como errado.

**O `QuestionService`** é o professor que escolhe as questões aleatoriamente. Ele não sabe nada sobre provas — só sabe buscar questões com os filtros que você pedir.

**O `QuizService`** é o coordenador de provas. Ele pede as questões pro professor (`QuestionService`), monta a prova (`Quiz` + `QuizQuestion`), recebe as respostas, corrige e gera o gabarito.

**A `FilterView`** é a tela inicial: você escolhe a matéria, o tópico e quantas questões. Quando envia o formulário, o coordenador monta sua prova e você vai para a sala de provas.

**A `PlayQuizView`** é a sala de provas: você vê todas as questões, marca suas respostas e quando clica em "Finalizar" o sistema corrige tudo de uma vez.

**A `ResultView`** é o gabarito: mostra o que você acertou (verde), errou (vermelho) e pulou (cinza), com a explicação de cada questão.

## Perguntas de entrevista

**P1. Por que usar `bulk_create` em vez de salvar cada objeto num loop?**
R: `bulk_create` faz **uma única query INSERT** com múltiplos valores, independente de quantos objetos. Um loop faria N queries ao banco — uma por objeto. Para 50 questões numa sessão de treino, a diferença entre 1 e 50 queries é 49x mais I/O. `bulk_create` é essencial para qualquer insert em lote.

**P2. O que é `select_related` e `prefetch_related`? Qual a diferença?**
R: Ambos evitam o problema N+1 (fazer uma query extra por objeto).
- `select_related` usa JOIN SQL — ideal para FKs (1:1 e N:1). Tudo numa query.
- `prefetch_related` faz uma query separada por relacionamento reverso (1:N, M:N) e une em Python. Ideal para `question.alternatives`.
Usar os dois juntos num prefetch profundo (`select_related("question__subject").prefetch_related("question__alternatives")`) é a combinação padrão para evitar N+1 em listas.

**P3. O que é o problema N+1 e como esta fase o evita?**
R: N+1 ocorre quando você faz 1 query para buscar N objetos e depois N queries para buscar dados relacionados (uma por objeto). No `get_result`, sem `prefetch_related("question__alternatives")`, cada questão faria uma query para buscar suas 4 alternativas — 50 questões = 50 queries extras. Com `prefetch_related`, são 2 queries no total.

**P4. Por que `@transaction.atomic` no `submit_answers`?**
R: Atomicidade. Se o `bulk_create` de `UserAnswer` falhar no meio (ex.: constraint violation), a transação faz rollback e o quiz não fica com status `finished` sem respostas gravadas. É tudo-ou-nada: ou todas as respostas são salvas E o quiz é marcado como finalizado, ou nada acontece.

**P5. Por que `is_correct` é calculado no submit e não recalculado toda vez?**
R: Imutabilidade do histórico. Se o gabarito de uma questão for corrigido depois, as respostas antigas do usuário não devem mudar retroativamente — isso distorceria as estatísticas de evolução. O valor gravado no momento do submit representa a verdade daquele instante.

**P6. Como funciona o sorteio aleatório das questões?**
R: `Question.objects.filter(...).order_by("?")` traduz para `ORDER BY RANDOM()` no PostgreSQL. O banco ordena aleatoriamente as linhas elegíveis antes de retornar. O slice `[:quantity]` então pega as N primeiras da lista aleatória.

**P7. Por que verificar `quiz.user == request.user` nas views?**
R: Autorização a nível de objeto. O Django protege rotas com `LoginRequiredMixin` (autenticação), mas não sabe que um quiz pertence a um usuário específico. Sem essa verificação, qualquer usuário logado poderia acessar `/questoes/treino/<uuid-de-outro-usuario>/` e ver ou submeter respostas no quiz alheio.

## O que aprendi nesta fase

**Django:**
- `FormView` com `form_valid()` para lógica pós-validação.
- `TemplateView` com GET e POST explícitos via `get()` e `post()`.
- `get_object_or_404` com múltiplos filtros para autorização.
- `select_related` vs `prefetch_related` — quando e por que usar cada um.
- `unique_together` em models — constraints de banco via ORM.
- `PROTECT` em FK — impede deleção de questões com histórico de resposta.
- `update_fields=["status", "finished_at"]` — update parcial eficiente.

**PostgreSQL:**
- `ORDER BY RANDOM()` para sorteio aleatório.
- `bulk_create` → único INSERT com múltiplas linhas (`INSERT INTO ... VALUES (...), (...), ...`).
- Índices compostos `(user, status)` para queries de listagem.

**Python:**
- `@dataclass` para objetos de transferência imutáveis e tipados.
- Dict comprehension `{ua.question_id: ua for ua in ...}` para lookup O(1).
- `str(uuid)` vs `uuid` — cuidado com tipos ao comparar PKs de model.

**Arquitetura:**
- Separação `QuestionService` (busca) vs `QuizService` (orquestração).
- Padrão "helper de autorização" (`_get_quiz_for_user`) centralizando segurança.
- Máquina de estados simples no model (`in_progress` → `finished`).
- Resultado como dataclass (objeto de transferência) em vez de dict.

**Testes:**
- Fixtures compostas (fixture `quiz` depende de `user`, `subject`, `questions`).
- Testar segurança: outro usuário deve receber 404.
- Testar idempotência: submit de quiz já finalizado não duplica respostas.
- Testar casos de borda: quantidade pedida maior que disponível, questões puladas.

## Resumo executivo

A Fase 5 entregou o fluxo completo de treino: **filtrar → resolver → ver resultado**. Criou o app `exams` com os models `Quiz`, `QuizQuestion` e `UserAnswer`; o `QuizService` com criação, submit e resultado; o `QuestionService` para sorteio aleatório; 3 templates Bootstrap 5 responsivos; e **21 testes novos (10 unitários + 11 integração)**, totalizando **54 testes passando** na suíte completa. Decisões-chave: `bulk_create` para performance, `ORDER BY RANDOM()` para sorteio, `is_correct` persistido no submit para integridade do histórico, e verificação de dono do quiz para segurança.

---

> **Próxima fase:** Fase 7 — Estatísticas e Pontos Fracos.

---
---

# FASE 6 — Dashboard

## Objetivo

Exibir uma **visão consolidada da evolução do usuário**: total de questões respondidas, acertos, erros, aproveitamento geral, sequência de dias de estudo (streak), progresso da meta diária e desempenho por disciplina.

## Problema que a fase resolve

O banco de questões (Fase 5) já gera dados de desempenho via `UserAnswer` e `Quiz`, mas esses dados estão dispersos no banco — o usuário não tem onde ver sua evolução. O dashboard cria o **ponto de entrada principal** do sistema: a tela que o usuário vê ao logar e que responde "como estou indo?".

## Arquivos criados

```
apps/dashboard/
├── __init__.py
├── apps.py
├── views.py          ← DashboardView (LoginRequired + TemplateView)
├── urls.py           ← / namespace="dashboard"
└── services/
    ├── __init__.py
    └── dashboard_service.py  ← DashboardService + DashboardStats + SubjectStat

templates/dashboard/
└── home.html         ← layout responsivo com cards, barras e treinos recentes

tests/
├── unit/test_dashboard_service.py      ← 11 testes
└── integration/test_dashboard_views.py ← 7 testes
```

## Arquivos modificados

- `config/settings/base.py` — `apps.dashboard` adicionado a `INSTALLED_APPS`.
- `config/urls.py` — `path("", ...)` adicionado como raiz.
- `templates/base.html` — navbar atualizada: brand → `dashboard:home`; links "Dashboard" e "Questões" adicionados.
- `docs/PROJECT_EXPLAINED.md` — status de fases 4, 5 e 6 corrigidos para ✅.

## Classes criadas

### `SubjectStat` (dataclass)
- **Função:** representa o desempenho de um usuário em uma disciplina específica — nome, cor, total respondido, total correto e percentual.
- **Por que existe?** Desacopla o resultado da query ORM da camada de apresentação. O template recebe um objeto tipado em vez de um dict com chaves longas como `question__subject__name`.

### `DashboardStats` (dataclass)
- **Função:** objeto de transferência com todas as métricas do dashboard.
- **Campos:**

| Campo | Tipo | Descrição |
|---|---|---|
| `total_answered` | int | Total de questões respondidas (todos os quizzes) |
| `total_correct` | int | Total de acertos |
| `total_wrong` | int | Total de erros |
| `total_quizzes` | int | Quantidade de treinos finalizados |
| `streak` | int | Sequência atual de dias consecutivos de estudo |
| `overall_percentage` | int | Aproveitamento geral (arredondado) |
| `subject_stats` | list[SubjectStat] | Desempenho por disciplina, ordenado por volume |
| `daily_goal` | int | Meta diária de questões (do perfil do usuário) |
| `today_answered` | int | Questões respondidas hoje |
| `today_remaining` | int | Faltam N questões para a meta de hoje |
| `daily_goal_percentage` | int | % da meta diária atingida (cap 100) |
| `recent_quizzes` | list | Últimos 5 treinos finalizados (anotados) |

### `DashboardService`
- **Responsabilidade:** calcular todas as métricas em queries otimizadas e retornar `DashboardStats`.
- **Por que existe?** A view não deve fazer queries — ela chama um service e repassa ao template.

**`get_stats(user) → DashboardStats`**
1. Uma query `aggregate` no `UserAnswer` filtrando por `quiz__user=user` → obtém `total` e `correct` num único round-trip.
2. `COUNT` no `Quiz` com `status=FINISHED` → `total_quizzes`.
3. `_compute_streak(user)` → streak.
4. `VALUES + ANNOTATE` no `UserAnswer` agrupando por disciplina → `subject_stats`.
5. `COUNT` no `UserAnswer` com `answered_at__date=today` → `today_answered`.
6. `ANNOTATE(correct_count, wrong_count)` nos últimos 5 quizzes → `recent_quizzes`.

**`_compute_streak(user) → int`**
1. Busca datas únicas de `Quiz.finished_at` em ordem decrescente via `.dates("finished_at", "day")`.
2. Se a data mais recente for mais de 1 dia atrás → `return 0` (streak quebrado).
3. Caminha a lista contando dias consecutivos a partir da data mais recente.
- **Regra:** streak válido se o usuário estudou **hoje ou ontem**. Assim a sequência sobrevive durante o dia atual mesmo que o usuário ainda não tenha estudado hoje.

## Views criadas

| View | Tipo base | URL | O que faz |
|---|---|---|---|
| `DashboardView` | `LoginRequiredMixin + TemplateView` | `GET /` | Chama `DashboardService.get_stats()` e renderiza o template |

## Template criado

### `dashboard/home.html`

Estrutura em três blocos condicionais:

**Estado vazio** (`total_answered == 0`): saudação, ícone de formatura e botão "Começar primeiro treino".

**Métricas principais** (4 cards em grade 2×2 mobile / 4 colunas desktop):
- Respondidas (azul), Acertos (verde), Erros (vermelho), Aproveitamento % (cor dinâmica: verde ≥70%, amarelo ≥50%, vermelho <50%).

**Métricas secundárias** (3 cards):
- 🔥 Streak com mensagem de incentivo quando zero.
- Treinos realizados.
- Meta diária: barra de progresso com badges `hoje_respondidas/meta` e texto "Meta atingida!" ou "Faltam N questões".

**Desempenho por disciplina** (grade 2 colunas desktop): para cada disciplina, nome + `correto/total — %` e barra colorida com a cor cadastrada na disciplina.

**Treinos recentes** (lista): até 5 treinos com disciplina, data, badges de acertos/erros e link "Ver" para o gabarito.

## Fluxo completo

```
1. Usuário acessa /                  → DashboardView.get()
2. LoginRequiredMixin verifica auth  → redireciona para /conta/login/ se não autenticado
3. get_context_data()
   └── DashboardService.get_stats(user)
       ├── aggregate(total, correct) em UserAnswer    → 1 query
       ├── count Quiz FINISHED                        → 1 query
       ├── _compute_streak()                          → 1 query (.dates())
       ├── values+annotate por disciplina             → 1 query
       ├── count UserAnswer hoje                      → 1 query
       └── annotate últimos 5 quizzes                 → 1 query
4. Template renderizado com DashboardStats
```

**Total de queries por acesso:** 6 — independente do volume de dados do usuário.

## Decisões arquiteturais

### Por que calcular streak em Python e não SQL puro?
A lógica de "dias consecutivos" envolve comparar a diferença entre datas sucessivas numa lista — isso é trivial em Python mas verboso em SQL puro (LAG, recursive CTE). A query `.dates()` busca apenas as datas únicas (uma por dia, sem repetição), que é um conjunto pequeno mesmo para usuários com meses de histórico. O loop Python é O(N) onde N = número de dias distintos de estudo.

### Por que `aggregate` em vez de dois `count` separados?
`aggregate(total=Count("id"), correct=Count("id", filter=...))` executa **uma única query SQL** com duas expressões de agregação. Dois `count()` separados fariam dois round-trips ao banco.

### Por que `today_remaining` no dataclass em vez de calcular no template?
Django templates não suportam aritmética (`daily_goal - today_answered`). Em vez de um template filter customizado, o valor é pré-computado no service — mantém a lógica no Python e o template limpo.

### Por que a URL do dashboard é `"/"` (raiz)?
O dashboard é a tela principal do sistema — faz sentido ser a URL raiz. `LOGIN_REDIRECT_URL = "dashboard:home"` já estava configurado na Fase 1 antecipando essa decisão.

### Por que não usar `UserSubjectStat` (modelo de agregação da Fase 2)?
O modelo `UserSubjectStat` foi planejado na Fase 2 como otimização futura para queries pesadas. Com 800 questões e um usuário, a query `VALUES + ANNOTATE` é instantânea — adicionar o modelo agora seria otimização prematura. Quando a Fase 7 (Estatísticas) exigir queries mais complexas, o modelo será introduzido.

## Explicação educacional

Imagine que você nunca viu este código.

**O `DashboardService`** é como o contador que vai ao banco de dados, some todos os números e volta com um relatório pronto. A view não faz queries — ela só pede o relatório e passa para o template.

**O `DashboardStats`** é o relatório em si: um objeto com todos os números que o template precisa. Por ser um `@dataclass`, é como um formulário preenchido — cada campo tem nome e tipo, é fácil de testar e não depende do ORM.

**O `_compute_streak`** funciona como um calendário: pega a lista de dias em que você estudou, começa pelo mais recente, e conta para trás enquanto os dias forem consecutivos. Se o dia mais recente foi há mais de ontem, a sequência está quebrada (voltou a zero).

**O `LoginRequiredMixin`** na view é a roleta de entrada: qualquer tentativa de acessar `/` sem estar logado é bloqueada e redirecionada para o login.

**As 6 queries** são eficientes porque nunca carregam dados em Python para depois filtrar — todo o trabalho pesado (`COUNT`, `GROUP BY`, `ORDER BY`) é feito no PostgreSQL.

## Perguntas de entrevista

**P1. Como o dashboard evita o problema N+1?**
R: Todas as métricas são calculadas com agregações no banco (`aggregate`, `annotate`, `count`) — nunca há loop em Python sobre objetos para contar ou somar. Os 5 treinos recentes usam `select_related("subject")` para evitar uma query extra por quiz ao acessar `quiz.subject.name`.

**P2. Por que usar `@dataclass` para `DashboardStats` em vez de um `dict`?**
R: Tipagem e legibilidade. `stats.total_correct` é mais claro que `stats["total_correct"]`, o `@dataclass` valida os campos na criação, e IDEs autocomplete os atributos. Além disso, testes podem asserir `stats.streak == 2` em vez de `stats.get("streak") == 2`.

**P3. Como funciona o cálculo de streak?**
R: `.dates("finished_at", "day")` retorna uma lista de datas únicas (sem duplicatas por dia) em ordem decrescente. O algoritmo verifica se a mais recente é hoje ou ontem (streak ativo). Depois percorre a lista contando dias consecutivos: se `date == expected`, incrementa e decrementa `expected` por um dia; se não, para.

**P4. Por que `today_remaining` está no dataclass e não calculado no template?**
R: Templates Django não suportam aritmética. `{{ stats.daily_goal - stats.today_answered }}` não funciona. A alternativa (filtro customizado `{% load dashboard_tags %}`) seria código extra desnecessário. Pré-calcular no service mantém o template limpo e o valor facilmente testável.

**P5. O que muda na navbar da Fase 6?**
R: A `brand` passou de `accounts:profile` para `dashboard:home` (agora o link mais importante). Foram adicionados links "Dashboard" e "Questões" na esquerda da navbar, seguindo o padrão de aplicações com múltiplas seções. O botão "Sair" permanece à direita.

## O que aprendi nesta fase

**Django:**
- `QuerySet.aggregate()` com múltiplas expressões — uma query, vários resultados.
- `QuerySet.values().annotate()` para `GROUP BY` em Python.
- `Count("id", filter=Q(...))` — agregação condicional (equivale ao `COUNT(CASE WHEN ...)` do SQL).
- `.dates("campo", "day")` para obter datas únicas de um DateTimeField.
- `TemplateView.get_context_data()` como ponto único de injeção de dados no template.

**PostgreSQL:**
- `COUNT(CASE WHEN is_correct THEN 1 END)` via `Count(filter=Q(...))`.
- `GROUP BY` via `.values().annotate()` — o Django gera o SQL correto automaticamente.

**Python:**
- `@dataclass` para objetos de transferência com múltiplos campos tipados.
- Algoritmo de streak: lista de datas decrescentes + contagem de consecutivos.

**Arquitetura:**
- Dashboard como "orquestrador de leitura" — agrega dados de `exams` e `questions` sem criar models próprios.
- Pré-computar valores derivados no service para manter o template declarativo.
- 6 queries por acesso são aceitáveis; `UserSubjectStat` só valerá quando houver necessidade comprovada.

**Testes:**
- Testar métricas zeradas para usuário novo (caso de borda crítico).
- Usar `quiz.save(update_fields=["finished_at"])` para simular treinos em datas passadas sem precisar de mocks de `timezone.now`.
- Testar `reverse("dashboard:home") == "/"` para garantir que a URL raiz está correta.

## Resumo executivo

A Fase 6 entregou o dashboard principal do Nícia Track: **6 queries por acesso**, **DashboardService** com métricas agregadas (total respondido, acertos, erros, aproveitamento, streak, meta diária, desempenho por disciplina, últimos 5 treinos), **1 view CBV** e **1 template Bootstrap 5 responsivo** com estado vazio, cards de métricas, barras de progresso coloridas por disciplina e lista de treinos recentes. A suíte cresceu de 54 para **72 testes (18 novos, todos passando)**.

---

> **Próxima fase:** Fase 8 — Simulados.

---
---

# FASE 7 — Estatísticas e Pontos Fracos

## Objetivo

Oferecer uma **página dedicada de análise de desempenho**: ranking de disciplinas (do mais fraco ao mais forte), ranking de pontos fracos e fortes por tópico, e visão de quais áreas precisam de mais atenção.

## Problema que a fase resolve

O dashboard (Fase 6) mostra um resumo de desempenho por disciplina, mas não responde "em qual tópico específico eu preciso melhorar?" nem apresenta um ranking claro de todas as disciplinas. Esta fase cria a **tela de análise profunda** — o usuário sai sabendo exatamente onde focar.

## Arquivos criados

```
apps/performance/
├── __init__.py
├── apps.py
├── views.py          ← PerformanceView (LoginRequired + TemplateView)
├── urls.py           ← /estatisticas/ namespace="performance"
└── services/
    ├── __init__.py
    └── performance_service.py  ← PerformanceService + dataclasses

templates/performance/
└── stats.html        ← tabela de disciplinas + cards de pontos fracos/fortes

tests/
├── unit/test_performance_service.py      ← 10 testes
└── integration/test_performance_views.py ← 6 testes
```

## Arquivos modificados

- `config/settings/base.py` — `apps.performance` adicionado a `INSTALLED_APPS`.
- `config/urls.py` — `path("estatisticas/", ...)` adicionado.
- `templates/base.html` — link "Estatísticas" adicionado à navbar.
- `docs/PROJECT_EXPLAINED.md` — Fase 7 documentada + status atualizado.

## Classes criadas

### `SubjectPerformance` (dataclass)
- **Função:** desempenho de um usuário em uma disciplina — nome, slug, cor, categoria (basic/specific), total respondido, total correto, percentual.

### `TopicPerformance` (dataclass)
- **Função:** desempenho em um tópico — nome, disciplina-pai (nome + cor), total, correto, percentual.

### `PerformanceStats` (dataclass)

| Campo | Tipo | Descrição |
|---|---|---|
| `subjects` | list[SubjectPerformance] | Disciplinas ordenadas por % crescente (pior → melhor) |
| `weak_topics` | list[TopicPerformance] | Bottom 5 tópicos (mín. 3 questões) |
| `strong_topics` | list[TopicPerformance] | Top 5 tópicos (mín. 3 questões) |
| `total_subjects_studied` | int | Disciplinas respondidas |
| `total_topics_studied` | int | Tópicos respondidos |
| `has_topic_data` | bool | Se há dados de tópico disponíveis |

### `PerformanceService`
- **Responsabilidade:** calcular stats de desempenho completo em 2 queries otimizadas.

**`get_full_stats(user) → PerformanceStats`**
1. `VALUES + ANNOTATE` no `UserAnswer` agrupando por campos de `subject` → subject stats.
2. `VALUES + ANNOTATE` no `UserAnswer` agrupando por `topic` (excluindo `isnull=True`) → topic stats.
3. Sort em Python por percentual ascendente.
4. Filtra `total >= MIN_QUESTIONS_FOR_RANKING (= 3)` → evita ruído de pouquíssimas questões.
5. `weak_topics = sorted[:5]`, `strong_topics = reversed[:5]`.

**`MIN_QUESTIONS_FOR_RANKING = 3`** — constante de módulo exportável para reutilização em testes sem hardcode.

## Views criadas

| View | Tipo base | URL | O que faz |
|---|---|---|---|
| `PerformanceView` | `LoginRequiredMixin + TemplateView` | `GET /estatisticas/` | Chama `PerformanceService.get_full_stats()` e renderiza o template |

## Template criado

### `performance/stats.html`

**Estado vazio** (`total_subjects_studied == 0`): ícone, mensagem e botão "Começar treino".

**Resumo** (2 cards): número de disciplinas estudadas + número de tópicos estudados.

**Tabela "Desempenho por disciplina"** (ordenada pior → melhor): badge de cor + badge basic/specific, colunas Respondidas / Acertos (coloridos por faixa) / Aproveitamento (progress bar inline).

**Cards laterais (col-md-6 cada):**
- **Pontos Fracos** (vermelho): bottom 5 tópicos qualificados, com nome, badge de disciplina, %, barra vermelha.
- **Pontos Fortes** (verde): top 5 tópicos, barra verde.
- Caso sem tópicos classificados: alerta informativo.

## Fluxo completo

```
1. Usuário acessa /estatisticas/       → PerformanceView.get()
2. LoginRequiredMixin verifica auth    → redireciona se não autenticado
3. get_context_data()
   └── PerformanceService.get_full_stats(user)
       ├── values+annotate por subject     → 1 query
       ├── values+annotate por topic       → 1 query
       └── sort + slice em Python          → 0 queries extras
4. Template renderizado com PerformanceStats
```

**Total de queries por acesso:** 2.

## Decisões arquiteturais

### Por que ordenar em Python e não no banco?
O Django não permite `ORDER BY` em colunas derivadas de `annotate` diretamente por alias sem subquery. Para listas de até 13 disciplinas, o sort em Python é O(N log N) com N minúsculo.

### Por que `MIN_QUESTIONS_FOR_RANKING = 3` e não 5?
Com tópicos distribuídos em 800 questões, um mínimo de 5 eliminaria quase todos os tópicos. 3 é o valor mínimo estatisticamente aceitável para inferir tendência.

### Por que `has_topic_data` no dataclass?
`weak_topics` pode estar vazio por dois motivos distintos: (a) não há tópicos nas questões respondidas, ou (b) há tópicos mas nenhum tem questões suficientes para o ranking. O template precisa distinguir esses casos para a mensagem correta.

### Por que `performance` app separado do `dashboard` app?
Conforme arquitetura da Fase 1: `dashboard` = resumo operacional (página inicial), `performance` = análise profunda. São responsabilidades distintas.

## Explicação educacional

**O `PerformanceService`** é como um auditor que pega todas as respostas e monta dois relatórios: um por disciplina e um por tópico. Usa `GROUP BY` do banco em 2 queries — sem carregar milhares de respostas em Python.

**Os pontos fracos e fortes** são calculados em Python: ordena a lista de tópicos por percentual, pega os 5 primeiros (piores) e os 5 últimos (melhores). O limiar mínimo evita que 1 acerto em 1 tentativa (100%) apareça como "ponto forte" enganosamente.

**A tabela ordenada do pior ao melhor** é intencional — o usuário precisa ver primeiro onde está mais fraco.

## Perguntas de entrevista

**P1. Como `values().annotate()` gera um `GROUP BY` no SQL?**
R: `values("campo__a", "campo__b")` instrui o Django a incluir esses campos no `SELECT` e no `GROUP BY`. O `annotate(Count("id"))` acrescenta a expressão de agregação. Resultado: `SELECT campo_a, campo_b, COUNT(id) FROM ... GROUP BY campo_a, campo_b`.

**P2. O que é `Count("id", filter=Q(is_correct=True))`?**
R: Agregação condicional — conta apenas os registros que satisfazem o filtro. Gera `COUNT(CASE WHEN is_correct = TRUE THEN 1 END)` no SQL. Permite contar total e corretos numa única query.

**P3. Por que o limiar `MIN_QUESTIONS_FOR_RANKING` é importante?**
R: Sem limiar, um tópico com 1 questão errada apareceria como 0% — o pior possível. Isso é ruído estatístico. O limiar garante que o ranking reflita uma tendência real.

**P4. Por que `has_topic_data` e não checar `weak_topics == []` no template?**
R: `weak_topics` pode estar vazio por dois motivos distintos — ausência de dados de tópico ou ausência de tópicos qualificados. A flag semântica evita lógica de negócio no template.

## O que aprendi nesta fase

**Django:** `values().annotate()` para `GROUP BY` com múltiplas colunas via `__` lookup. `Count(filter=Q(...))` para agregação condicional.

**Python:** `sorted(list, key=lambda x: x.field)` + `list(reversed(...))`. Constante de módulo exportável.

**Arquitetura:** Separação dashboard (resumo) vs performance (análise). Limiar mínimo de qualidade para rankings. Flag semântica vs checar lista vazia.

**Testes:** Criar questões com e sem tópicos para cobrir os dois fluxos. Verificar ordenação e limites de ranking.

## Resumo executivo

A Fase 7 entregou `/estatisticas/` com **2 queries por acesso**, **PerformanceService** com ranking de disciplinas (pior → melhor) e ranking de pontos fracos/fortes por tópico (mínimo 3 questões), **1 view CBV** e **1 template Bootstrap 5 responsivo** com tabela de disciplinas colorida, cards de pontos fracos/fortes e estado vazio. A suíte cresceu de 72 para **88 testes (16 novos, todos passando)**.

---

> **Próxima fase:** Fase 9 — Qualidade.

---
---

# FASE 8 — Simulados

## Objetivo

Simular a prova real do Concurso 003/2026 (Prefeitura de Ponta Grossa/PR, banca Instituto UniFil): **40 questões** com distribuição exata por disciplina, cronômetro de 3 horas, preservação de progresso via `localStorage` e resultado detalhado por disciplina.

## Problema que a fase resolve

O usuário pode treinar questões por disciplina (Fase 5), mas não consegue simular as condições reais da prova — distribuição específica, tempo limitado e resultado por área. Esta fase cria o **modo exame** completo.

## Distribuição da prova

| Disciplina | Tipo | Questões |
|---|---|---|
| Português | Básica | 5 |
| Matemática | Básica | 5 |
| Informática | Básica | 5 |
| Conhecimentos Gerais | Básica | 5 |
| Conhecimentos Específicos | Específica | 20 |
| **Total** | | **40** |

## Arquivos criados

```
apps/exams/services/
└── simulated_service.py   ← SimulatedService + InsufficientQuestionsError

templates/exams/
├── simulated_start.html   ← landing page com distribuição e CTA
└── simulated_play.html    ← prova com cronômetro e localStorage

tests/
├── unit/test_simulated_service.py       ← 9 testes
└── integration/test_simulated_views.py  ← 10 testes
```

## Arquivos modificados

- `apps/exams/views.py` — adicionados `SimulatedStartView`, `SimulatedPlayView`; `ResultView` atualizado com breakdown de simulado.
- `apps/exams/urls.py` — 2 novas URLs (`/questoes/simulado/` e `/questoes/simulado/<uuid>/`).
- `templates/exams/result.html` — breakdown por disciplina + título "Simulado" + botão "Novo simulado".
- `templates/base.html` — link "Simulado" adicionado à navbar.
- `docs/PROJECT_EXPLAINED.md` — Fase 8 documentada + status atualizado.

## Constantes

```python
BASIC_PER_SUBJECT = 5       # questões por disciplina básica
SPECIFIC_TOTAL = 20         # questões específicas
SIMULATED_TOTAL = 40        # total
TIME_LIMIT_MINUTES = 180    # 3 horas
```

## Classes criadas

### `InsufficientQuestionsError(DomainException)`
- **Função:** exceção de domínio lançada quando não há questões suficientes no banco para montar um simulado.
- **Por que existe?** Separar erros de domínio de erros técnicos; a view a captura e exibe como `messages.error`.

### `SimulatedService`

**`get_in_progress(user) → Quiz | None`**
- Busca o simulado `IN_PROGRESS` do usuário. Retorna `None` se não há nenhum.
- Usado na `SimulatedStartView` para evitar criar dois simulados simultâneos.

**`create_simulated_quiz(user) → Quiz`**
1. Busca as 4 disciplinas básicas ativas.
2. Para cada uma: sorteia 5 questões via `ORDER BY RANDOM()` — levanta `InsufficientQuestionsError` se houver menos de 5.
3. Sorteia 20 questões da pool de todas as disciplinas específicas — levanta `InsufficientQuestionsError` se houver menos de 20.
4. Junta as 40 questões, faz `random.shuffle` em Python, cria `Quiz(quiz_type=SIMULATED)` e `bulk_create` dos `QuizQuestion`.
5. `@transaction.atomic` — tudo ou nada.

**`get_subject_breakdown(quiz) → list[dict]`**
- Uma query `VALUES + ANNOTATE` sobre `UserAnswer` do quiz → total e acertos por disciplina.
- Usada pela `ResultView` para mostrar desempenho por área no resultado do simulado.

## Views criadas

| View | URL | O que faz |
|---|---|---|
| `SimulatedStartView` | `GET/POST /questoes/simulado/` | GET: mostra landing page (ou redireciona se há simulado ativo); POST: cria simulado e redireciona |
| `SimulatedPlayView` | `GET/POST /questoes/simulado/<uuid>/` | GET: exibe as 40 questões com cronômetro; POST: submete respostas |

`ResultView` foi extendido: quando `quiz.quiz_type == SIMULATED`, injeta `subject_breakdown` no contexto.

## Templates criados

### `simulated_start.html`
Card centralizado com:
- Ícone, título e banca do concurso.
- 2 badges: "40 questões" e "3h".
- Lista de distribuição com cores das disciplinas.
- Alerta de atenção ("cronômetro começa ao iniciar; fechar e retornar preserva respostas").
- Botão "Iniciar simulado" (POST).

### `simulated_play.html`
- **Cabeçalho sticky** (abaixo da navbar, `top: 70px`): título, contagem de questões, cronômetro em tempo real e botão "Finalizar".
- **Badge de disciplina** acima de cada questão (cor da disciplina).
- **JavaScript (IIFE):**
  - Timer: `setInterval(1000)` com contagem regressiva; vermelhor nos últimos 5 min; auto-submit ao chegar a 0; persiste em `localStorage[timer_<uuid>]`.
  - Respostas: salva seleções em `localStorage[answers_<uuid>]` a cada mudança; restaura ao recarregar a página.
  - Navegação: botões de atalho ficam azuis sólidos quando a questão é respondida.
  - `finalizarSimulado()`: confirma questões sem resposta antes de submeter; limpa localStorage ao confirmar.

### `result.html` (modificado)
- Título: "Simulado" em vez de `quiz.subject.name` quando `quiz_type == simulated`.
- Nova seção **"Resultado por disciplina"** (antes do gabarito): grid de barras por disciplina com cor dinâmica.
- Botão de ação: "Novo simulado" (→ `simulated_start`) no lugar de "Treinar novamente" para simulados.

## Fluxo completo

```
1. Usuário clica "Simulado" na navbar        → SimulatedStartView.get()
   ├── Se há simulado ativo                  → redirect para simulated_play
   └── Else                                  → renderiza simulated_start.html

2. Clica "Iniciar simulado"                  → SimulatedStartView.post()
   └── SimulatedService.create_simulated_quiz()
       ├── 4× ORDER BY RANDOM() LIMIT 5      → 4 queries (básicas)
       ├── ORDER BY RANDOM() LIMIT 20         → 1 query (específicas)
       └── bulk_create 40 QuizQuestions       → 1 query
   └── redirect → simulated_play

3. Responde questões                         → SimulatedPlayView.get()
   ├── Cronômetro JS conta regressivamente
   ├── Seleções salvas em localStorage
   └── Botões de navegação ficam sólidos

4. Clica "Finalizar" ou timer expira         → SimulatedPlayView.post()
   └── QuizService.submit_answers()
   └── redirect → ResultView

5. Resultado                                 → ResultView.get()
   ├── QuizService.get_result()              → gabarito por questão
   └── SimulatedService.get_subject_breakdown() → desempenho por disciplina
```

## Decisões arquiteturais

### Por que duas etapas de aleatoriedade (ORDER BY RANDOM + random.shuffle)?
`ORDER BY RANDOM()` no banco sorteia eficientemente N questões de cada pool (básica por disciplina, específicas total). O `random.shuffle` em Python mistura as questões das diferentes disciplinas — sem isso, as 20 básicas viriam todas agrupadas antes das 20 específicas.

### Por que criar `SimulatedStartView` separada de `FilterView`?
Responsabilidades diferentes: `FilterView` recebe parâmetros do usuário (disciplina, quantidade); `SimulatedStartView` não tem parâmetros — o serviço decide tudo. Fundir as duas criaria uma view com lógica condicional complexa.

### Por que `localStorage` para cronômetro e respostas?
O cronômetro precisa persistir entre recargas de página (o usuário pode fechar acidentalmente e retornar). Usar uma solução server-side exigiria endpoint extra e estado no banco. `localStorage` é suficiente para este caso — se o usuário trocar de dispositivo, o timer reinicia, mas o quiz ainda está em andamento (o prazo é controlado pelo servidor quando implementar expiração futura).

### Por que `get_in_progress` redireciona em vez de criar novo quiz?
Evita que o usuário acumule simulados não finalizados. Se há um em andamento, deve terminá-lo — é o comportamento esperado de uma prova.

### Por que `InsufficientQuestionsError` em vez de retornar `None`?
A ausência de questões é um erro de configuração (banco não importado), não um estado normal. Uma exceção de domínio capturável na view é mais expressiva que um valor `None` que a view teria de checar e tratar silenciosamente.

## Explicação educacional

**O `SimulatedService`** é como o coordenador de provas: ele monta a prova respeitando o edital (4×5 básicas + 20 específicas), embaralha as questões para que não fiquem agrupadas por matéria, e cria o "caderno de provas" (o `Quiz`) atomicamente.

**O cronômetro JavaScript** é o fiscal de sala digital: conta regressivamente, fica vermelho nos últimos 5 minutos e entrega a prova automaticamente quando o tempo acaba. O `localStorage` é o caderno de rascunho — preserva as marcações do candidato se ele sair e voltar, mas é apagado ao entregar.

**O breakdown por disciplina** no resultado é o espelho da correção real: mostra quantas questões o candidato acertou em cada área, permitindo identificar onde precisa reforçar.

## Perguntas de entrevista

**P1. Como o simulado garante a distribuição exata (5+5+5+5+20)?**
R: `SimulatedService.create_simulated_quiz` faz 4 queries separadas — uma por disciplina básica com `ORDER BY RANDOM() LIMIT 5` — e uma query para as específicas com `LIMIT 20`. Cada query tem seu LIMIT explícito; se qualquer uma retornar menos que o esperado, `InsufficientQuestionsError` é lançado antes de criar qualquer coisa.

**P2. Por que usar `@transaction.atomic` na criação do simulado?**
R: O `Quiz` e os 40 `QuizQuestion` precisam ser criados como unidade. Se o `bulk_create` falhar (ex.: constraint violation), o Quiz não pode ficar sem questões. A transação garante tudo-ou-nada.

**P3. Como o cronômetro funciona e por que `localStorage`?**
R: Um `setInterval` de 1 segundo decrementa o contador e salva o valor em `localStorage`. Na próxima abertura da página, o timer lê o valor salvo em vez de começar do início. Quando chega a zero, o formulário é submetido automaticamente. `localStorage` é a solução mais simples para persistir estado client-side entre recargas sem custo de servidor.

**P4. O que acontece se o usuário tentar criar um novo simulado com um já em andamento?**
R: `SimulatedStartView.get()` e `.post()` chamam `SimulatedService.get_in_progress()` antes de criar qualquer coisa. Se houver um quiz `in_progress` do tipo `simulated`, o usuário é redirecionado para ele — nunca é criado um segundo simulado simultâneo.

**P5. Como o `result.html` distingue treino de simulado?**
R: A `ResultView` injeta `subject_breakdown` no contexto apenas quando `quiz.quiz_type == Quiz.SIMULATED`. O template verifica `{% if subject_breakdown %}` para exibir a seção extra. Para o título e os botões de ação, o template verifica `{% if quiz.quiz_type == "simulated" %}` diretamente.

## O que aprendi nesta fase

**Django:**
- `View` genérico com `get()` e `post()` separados (sem `FormView`) para lógica mais explícita.
- Importação local dentro de método (`from django.shortcuts import render`) para evitar circular imports.
- Injetar contexto extra em views existentes condicionalmente (`subject_breakdown` apenas para simulados).

**JavaScript:**
- IIFE `(function(){})()` para escopo isolado sem poluir o global.
- `localStorage.getItem` / `setItem` / `removeItem` para persistência client-side.
- `setInterval` + auto-submit para timer de prova.
- Restaurar estado de formulário (radio buttons) a partir de dados salvos.

**Arquitetura:**
- Separação de concerns: `SimulatedService` monta a prova; `QuizService.submit_answers` corrige (reuso sem duplicação).
- `InsufficientQuestionsError` como exceção de domínio — a view captura e exibe; o service não sabe nada de HTTP.
- `get_in_progress` como guard — previne estado inconsistente antes de qualquer ação.

**Testes:**
- Fixture `full_bank` criando o banco mínimo necessário (4 básicas + 1 específica com questões suficientes).
- Testar distribuição: contar questões por categoria após criar o simulado.
- Testar guards: `get_in_progress` retorna None para quiz finalizado; redireciona para ativo.
- Testar integração completa: criar → jogar → submeter → ver resultado com breakdown.

## Resumo executivo

A Fase 8 entregou o **modo simulado completo**: `SimulatedService` com criação atômica de 40 questões (5+5+5+5+20), `SimulatedStartView` com guard de simulado ativo, `SimulatedPlayView` com cronômetro JavaScript + `localStorage` para persistir timer e respostas, e resultado com breakdown por disciplina. A suíte cresceu de 88 para **107 testes (19 novos, todos passando)**.

---

> **Próxima fase:** Fase 9 — Qualidade.
