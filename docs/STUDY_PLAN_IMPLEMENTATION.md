# STUDY_PLAN_IMPLEMENTATION.md
# Plano de Estudos — Documento Técnico de Implementação

> **Status:** Aguardando aprovação. Nenhum código será escrito antes da aprovação deste documento.
> **Data:** 2026-06-30
> **Sistema base:** Nícia Track (10 fases concluídas, deploy em produção)

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Fluxo do Usuário](#3-fluxo-do-usuário)
4. [Banco de Dados](#4-banco-de-dados)
5. [Rotas (URLs)](#5-rotas-urls)
6. [Templates](#6-templates)
7. [Integrações](#7-integrações)
8. [Plano de Implementação](#8-plano-de-implementação)
9. [Impacto no Sistema Atual](#9-impacto-no-sistema-atual)
10. [Estimativa Final](#10-estimativa-final)

---

## 1. Visão Geral

### O problema

O sistema Nícia Track possui um banco de 800 questões, simulados e estatísticas — mas não guia a candidata no **estudo ativo do conteúdo**. A candidata sabe _o que_ errou, mas não tem onde estudar _o que_ precisa aprender. Os 14 arquivos MASTER existem em `docs/`, mas são documentos estáticos, impossíveis de rastrear ou interagir.

### A solução proposta

Criar um novo app Django chamado `study_plan` que transforma os 14 arquivos MASTER em uma **experiência guiada de estudo** — com controle de progresso por capítulo, aprendizagem ativa, reflexão guiada, mini quizzes, caderno de erros e sistema de streak.

A metáfora central é: **o sistema é um professor, não uma biblioteca**. Em vez de abrir um arquivo gigante, a candidata recebe o conteúdo em doses diárias estruturadas, com interação após cada lição.

### Princípios de design

- **Reutilização máxima:** modelos e serviços existentes são reaproveitados sempre que possível. O mini quiz reutiliza o app `exams`; o caderno de erros consome `UserAnswer` existente; o streak estende o que já existe no dashboard.
- **Consistência arquitetural:** novo app segue exatamente o padrão já estabelecido — `BaseModel` (UUID), Service Layer, CBV, templates Bootstrap 5.
- **Conteúdo como dados:** os capítulos dos MASTER são importados via management command (mesmo padrão do `import_questions`), tornando o conteúdo consultável, filtrável e ligado ao banco de questões.
- **Zero perfeccionismo:** não implementar o que não foi aprovado. Áudio é analisado, não construído. Mini quiz usa questões existentes antes de criar um modelo próprio.

---

## 2. Arquitetura

### Novo app: `apps/study_plan/`

O novo app segue a mesma estrutura dos apps existentes:

```
apps/study_plan/
├── __init__.py
├── apps.py
├── admin.py
├── models.py                    ← 6 novos models
├── forms.py                     ← formulários de reflexão e nota
├── urls.py                      ← /plano/ namespace="study_plan"
├── views.py                     ← 8 views CBV
├── migrations/
├── management/
│   └── commands/
│       └── import_study_plan.py ← popula StudyModule + StudyChapter
└── services/
    ├── __init__.py
    ├── plan_service.py          ← progresso, próximo capítulo, stats
    ├── mini_quiz_service.py     ← geração do mini quiz
    └── error_notebook_service.py ← lógica do caderno de erros
```

### Posição na arquitetura de camadas existente

```
┌─────────────────────────────────────────────────────────┐
│ Presentation — Templates Bootstrap 5 (+ HTMX opcional)   │
├─────────────────────────────────────────────────────────┤
│ View Layer — CBV (LoginRequiredMixin)                     │
├─────────────────────────────────────────────────────────┤
│ Service Layer                                             │
│  ├── PlanService (progresso, agenda diária)              │
│  ├── MiniQuizService (seleção de questões do banco)      │
│  └── ErrorNotebookService (consolidação de erros)        │
├─────────────────────────────────────────────────────────┤
│ ORM (novos models + models reutilizados)                  │
│  Novos: StudyModule, StudyChapter, LessonProgress,       │
│         ActiveLearningNote, GuidedReflection,            │
│         ErrorNotebookEntry                               │
│  Reutilizados: Quiz, QuizQuestion, UserAnswer,           │
│                Question, Subject, User, StudySession     │
└─────────────────────────────────────────────────────────┘
```

### Models reutilizados (sem alteração)

| Model | App de origem | Como é reutilizado |
|---|---|---|
| `User` | accounts | FK em todos os novos models |
| `Subject` | questions | FK em `StudyModule` (liga módulo à disciplina) |
| `Question` | questions | FK em `ErrorNotebookEntry`; selecionada pelo MiniQuizService |
| `Quiz` | exams | Mini quiz cria um `Quiz` com `quiz_type="mini"` |
| `QuizQuestion` | exams | Usado pelo mini quiz normalmente |
| `UserAnswer` | exams | FK em `ErrorNotebookEntry` (rastreia o erro específico) |
| `StudySession` | performance | Extendido com referência ao capítulo estudado |

### Models alterados (mudanças mínimas)

| Model | Alteração | Motivo |
|---|---|---|
| `Quiz` | Novo valor no `TYPE_CHOICES`: `MINI = "mini"` e `chapter = FK(StudyChapter, null=True)` | Identificar quizzes gerados pelo plano e ligar ao capítulo |

> **Nota:** adicionar uma FK nullable em `Quiz` é uma migration segura (sem `NOT NULL`, sem reescrever dados). O comportamento do restante do sistema não muda.

---

## 3. Fluxo do Usuário

### 3.1 Acesso inicial ao Plano de Estudos

```
1. Usuária clica em "Plano de Estudos" na navbar
2. Sistema verifica se existe progresso salvo
   ├── Sem progresso → exibe dashboard do plano com estado inicial
   │                   + botão "Começar a estudar hoje"
   └── Com progresso → exibe dashboard personalizado:
                       semana atual, dia atual, próximo capítulo,
                       % de conclusão geral, streak do plano
```

### 3.2 Dashboard do Plano (tela principal)

A tela exibe:
- **Card "Hoje":** semana, dia, fase atual (1–4), conteúdo previsto, tempo estimado
- **Card "Progresso geral":** barra com % de capítulos concluídos de todos os módulos
- **Card "Streak do plano":** dias consecutivos com pelo menos 1 capítulo concluído
- **Lista de módulos:** todos os 14 módulos com status (não iniciado / em andamento / concluído) e % individual
- **Botão de ação primário:** "Continuar de onde parei" → vai direto ao próximo capítulo pendente

### 3.3 Dentro de um Módulo

```
Usuária clica em "Saúde Única"
→ Tela do módulo: título, descrição, tempo estimado total,
  lista de capítulos com status individual
→ Clica em um capítulo disponível
```

### 3.4 Fluxo de Estudo de um Capítulo (fluxo principal)

```
ETAPA 1 — Leitura
├── Sistema exibe o conteúdo do capítulo (markdown renderizado)
├── Barra de progresso de leitura (scroll-based, JS simples)
└── Botão "Concluí a leitura" (somente após rolar até o fim)

ETAPA 2 — Aprendizagem Ativa
├── Campo de texto: "Explique com suas palavras o que aprendeu neste capítulo"
├── Campo obrigatório (mínimo 20 caracteres)
└── Botão "Salvar e continuar"

ETAPA 3 — Reflexão Guiada
├── Pergunta 1: "O que você entendeu neste capítulo?"
├── Pergunta 2: "Qual foi a parte mais importante?"
├── Pergunta 3: "Qual foi a parte mais difícil ou que gerou dúvida?"
└── Botão "Salvar reflexão"

ETAPA 4 — Mini Quiz
├── Sistema seleciona 3–5 questões do banco relacionadas ao tema do capítulo
├── Exibição idêntica ao play.html existente (reutilizado)
├── Usuária responde e finaliza
└── Sistema exibe resultado imediato + gabarito comentado

ETAPA 5 — Questões Sugeridas (transição)
├── "Você estudou Raiva — que tal praticar com mais questões?"
├── Botão "Treinar questões de [tema]" → cria quiz no app exams com filtro
└── Botão "Próximo capítulo" → avança no módulo
```

### 3.5 Caderno de Erros

```
Usuária acessa /plano/caderno-de-erros/
→ Lista de todas as questões erradas (de treinos e simulados)
→ Ordenadas por: mais erradas primeiro, mais recentes primeiro
→ Para cada entrada: questão, resposta dada, resposta correta,
  número de vezes errada, data do último erro, campo de anotação pessoal
→ Botão "Revisar" → abre a questão em modo leitura com gabarito
→ Botão "Marcar como revisada" → não some da lista, mas muda status
```

### 3.6 Página de Streak

```
Usuária acessa /plano/progresso/
→ Calendário visual do mês (dia = verde se estudou, cinza se não estudou)
→ Métricas: maior streak, streak atual, dias estudados total,
  horas estudadas, capítulos concluídos, resumos escritos
```

---

## 4. Banco de Dados

### 4.1 Tabela `study_module` (StudyModule)

Representa um dos 14 arquivos MASTER. Cada módulo corresponde a uma disciplina.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | Herdado de BaseModel |
| `subject` | FK(Subject, null=True) | Liga ao Subject do app questions (pode ser null para MASTER sem Subject equivalente) |
| `title` | CharField(200) | Ex.: "Saúde Única", "Zoonoses e Vigilância" |
| `slug` | SlugField(unique=True) | Ex.: "saude-unica", "zoonoses-vigilancia" |
| `order` | PositiveSmallIntegerField | Ordem de estudo (1–14) conforme PLANO_DE_ESTUDOS_MASTER |
| `description` | TextField(blank=True) | Descrição do módulo |
| `master_file` | CharField(50) | Ex.: "01_SAUDE_UNICA_MASTER" — referência ao arquivo de origem |
| `study_phase` | CharField(10) | Fase prevista: "1", "2", "3", "4" |
| `estimated_hours` | DecimalField(4,1) | Horas previstas no PLANO_DE_ESTUDOS_MASTER |
| `category` | CharField(10) | "specific" ou "basic" (herdado do Subject se vinculado) |
| `icon` | CharField(10, blank=True) | Emoji opcional para visualização |
| `is_active` | BooleanField | Soft toggle |
| `created_at` | DateTimeField | Herdado de BaseModel |
| `updated_at` | DateTimeField | Herdado de BaseModel |

**Índices:** `(order)`, `(category)`, `(study_phase)`

---

### 4.2 Tabela `study_chapter` (StudyChapter)

Representa um capítulo/seção dentro de um módulo. Um módulo tem N capítulos.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | Herdado de BaseModel |
| `module` | FK(StudyModule, CASCADE) | Módulo pai |
| `title` | CharField(200) | Ex.: "One Health — Conceito e Definição OHHLEP" |
| `slug` | SlugField | Ex.: "one-health-conceito" (único dentro do módulo) |
| `order` | PositiveSmallIntegerField | Sequência dentro do módulo |
| `content` | TextField | Conteúdo em markdown (importado do MASTER) |
| `key_points` | TextField(blank=True) | Resumo dos pontos-chave (extraído do MASTER) |
| `estimated_minutes` | PositiveSmallIntegerField | Tempo estimado de leitura em minutos |
| `related_subjects` | ManyToManyField(Subject, blank=True) | Subjects relacionados (para sugestão de questões) |
| `is_active` | BooleanField | Soft toggle |
| `created_at` | DateTimeField | Herdado de BaseModel |
| `updated_at` | DateTimeField | Herdado de BaseModel |

**Constraints:** `unique_together = [('module', 'slug')]`, `unique_together = [('module', 'order')]`

**Índices:** `(module, order)`, `(module, is_active)`

---

### 4.3 Tabela `lesson_progress` (LessonProgress)

Rastreia o progresso individual de cada usuária por capítulo.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | Herdado de BaseModel |
| `user` | FK(User, CASCADE) | Usuária |
| `chapter` | FK(StudyChapter, CASCADE) | Capítulo |
| `status` | CharField(15) | `"not_started"` / `"in_progress"` / `"completed"` |
| `started_at` | DateTimeField(null=True) | Quando iniciou a leitura |
| `completed_at` | DateTimeField(null=True) | Quando marcou como concluído |
| `time_spent_minutes` | PositiveSmallIntegerField(default=0) | Tempo acumulado na leitura |
| `created_at` | DateTimeField | Herdado de BaseModel |
| `updated_at` | DateTimeField | Herdado de BaseModel |

**Constraints:** `unique_together = [('user', 'chapter')]`

**Índices:** `(user, status)`, `(user, chapter)`, `(user, completed_at)`

---

### 4.4 Tabela `active_learning_note` (ActiveLearningNote)

Armazena a explicação livre da usuária após ler um capítulo ("explique com suas palavras").

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | Herdado de BaseModel |
| `user` | FK(User, CASCADE) | Usuária |
| `chapter` | FK(StudyChapter, CASCADE) | Capítulo estudado |
| `explanation` | TextField | Texto livre da usuária (mínimo 20 chars, validado no form) |
| `created_at` | DateTimeField | Herdado de BaseModel |
| `updated_at` | DateTimeField | Data da última edição |

**Constraints:** `unique_together = [('user', 'chapter')]` — uma nota por capítulo; edição sobrescreve.

---

### 4.5 Tabela `guided_reflection` (GuidedReflection)

Armazena as 3 respostas da reflexão guiada por capítulo.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | Herdado de BaseModel |
| `user` | FK(User, CASCADE) | Usuária |
| `chapter` | FK(StudyChapter, CASCADE) | Capítulo estudado |
| `what_understood` | TextField | "O que você entendeu?" |
| `most_important` | TextField | "Qual foi a parte mais importante?" |
| `most_difficult` | TextField | "Qual foi a parte mais difícil?" |
| `created_at` | DateTimeField | Herdado de BaseModel |
| `updated_at` | DateTimeField | Data da última edição |

**Constraints:** `unique_together = [('user', 'chapter')]`

---

### 4.6 Tabela `error_notebook_entry` (ErrorNotebookEntry)

Centraliza e enriquece as questões erradas. Consome `UserAnswer` existente.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | Herdado de BaseModel |
| `user` | FK(User, CASCADE) | Usuária |
| `question` | FK(Question, PROTECT) | A questão errada |
| `last_user_answer` | FK(UserAnswer, null=True, SET_NULL) | Última resposta errada (ponteiro atualizado a cada novo erro) |
| `wrong_count` | PositiveSmallIntegerField(default=1) | Total de vezes errada |
| `last_wrong_at` | DateTimeField | Data do último erro |
| `next_review_at` | DateField(null=True) | Data da próxima revisão sugerida (revisão espaçada simples) |
| `personal_note` | TextField(blank=True) | Anotação livre da candidata |
| `is_reviewed` | BooleanField(default=False) | Foi revisada ativamente ao menos uma vez |
| `created_at` | DateTimeField | Herdado de BaseModel |
| `updated_at` | DateTimeField | Herdado de BaseModel |

**Constraints:** `unique_together = [('user', 'question')]` — uma entrada por questão; `wrong_count` é incrementado a cada novo erro.

**Índices:** `(user, next_review_at)`, `(user, wrong_count DESC)`, `(user, is_reviewed)`

**Lógica de `next_review_at`:**
- 1º erro → revisar em D+1
- 2º erro → revisar em D+3
- 3º erro → revisar em D+7
- 4º+ erro → revisar em D+14
(Revisão espaçada simplificada, calculada no service)

---

### 4.7 Alteração no model `Quiz` existente (apps/exams/models.py)

```
Adicionar:
  MINI = "mini"
  TYPE_CHOICES += [(MINI, "Mini Quiz")]
  chapter = FK(StudyChapter, null=True, blank=True, on_delete=SET_NULL)
```

Esta é a única alteração em model existente. A FK é nullable, então todos os quizzes já existentes (practice/simulated) não são afetados. A migration é segura.

---

### 4.8 Diagrama de relacionamentos completo (novos + reutilizados)

```
User ──1:N── LessonProgress ──N:1── StudyChapter ──N:1── StudyModule
  │                                      │                    │
  ├──1:N── ActiveLearningNote ───────────┘                    │
  │                                                           │
  ├──1:N── GuidedReflection ─────────────┘               FK(Subject)
  │                                                       (reutilizado)
  ├──1:N── ErrorNotebookEntry ──FK(Question)
  │              └──FK(UserAnswer)              StudyChapter
  │                                              └──M:N── Subject
  └──1:N── Quiz ──(quiz_type="mini")──────────FK(StudyChapter)
               └──1:N── QuizQuestion ──N:1── Question
               └──1:N── UserAnswer
```

---

## 5. Rotas (URLs)

Novo arquivo: `apps/study_plan/urls.py` com namespace `"study_plan"`

Incluído em `config/urls.py` com:
```
path("plano/", include("apps.study_plan.urls", namespace="study_plan"))
```

### URLs do app study_plan

| URL | Nome | View | Descrição |
|---|---|---|---|
| `/plano/` | `dashboard` | `PlanDashboardView` | Dashboard principal do plano |
| `/plano/modulos/` | `module_list` | `ModuleListView` | Lista todos os 14 módulos |
| `/plano/modulo/<slug>/` | `module_detail` | `ModuleDetailView` | Detalhe do módulo com lista de capítulos |
| `/plano/capitulo/<slug>/` | `chapter_read` | `ChapterReadView` | Conteúdo do capítulo (leitura) |
| `/plano/capitulo/<slug>/concluir/` | `chapter_complete` | `ChapterCompleteView` | POST: marca capítulo como concluído |
| `/plano/capitulo/<slug>/nota/` | `chapter_note` | `ChapterNoteView` | GET/POST: aprendizagem ativa |
| `/plano/capitulo/<slug>/reflexao/` | `chapter_reflection` | `ChapterReflectionView` | GET/POST: reflexão guiada (3 perguntas) |
| `/plano/capitulo/<slug>/mini-quiz/` | `chapter_mini_quiz` | `ChapterMiniQuizView` | GET: inicia mini quiz; POST: cria Quiz no banco |
| `/plano/caderno-de-erros/` | `error_notebook` | `ErrorNotebookView` | Lista do caderno de erros |
| `/plano/caderno-de-erros/<uuid>/nota/` | `error_note` | `ErrorNoteView` | POST: salva anotação em uma entrada |
| `/plano/caderno-de-erros/<uuid>/revisar/` | `error_review` | `ErrorReviewView` | POST: marca como revisada |
| `/plano/progresso/` | `progress` | `ProgressView` | Streak e calendário visual |

**Total: 12 URLs novas** (mais os redirects internos do fluxo de capítulo)

---

## 6. Templates

Novos templates em `templates/study_plan/`:

### 6.1 `study_plan/dashboard.html`

**Herda:** `base.html`

**Conteúdo:**
- Card "Hoje": semana/dia/fase atual, conteúdo do dia, horas previstas
- Barra de progresso geral (% capítulos concluídos)
- Card streak (dias consecutivos no plano)
- Grade de módulos (cards com ícone, título, % de conclusão, badge de fase)
- Botão primário "Continuar de onde parei" (destaque no topo)
- Estado vazio: se não há progresso, exibe mensagem motivacional + botão "Começar o Módulo 1"

### 6.2 `study_plan/module_list.html`

**Herda:** `base.html`

**Conteúdo:**
- Separados em 2 seções: "Específicos" e "Básicas"
- Card por módulo: ícone, título, N capítulos, % conclusão, tempo estimado, badge de fase
- Status visual: cadeado (bloqueado), play (disponível), check (concluído)

### 6.3 `study_plan/module_detail.html`

**Herda:** `base.html`

**Conteúdo:**
- Header: título do módulo, Subject vinculado, horas estimadas, % conclusão
- Lista de capítulos com status (não iniciado / em andamento / concluído), tempo estimado de cada um
- Breadcrumb: Plano → Módulo

### 6.4 `study_plan/chapter_read.html`

**Herda:** `base.html`

**Conteúdo:**
- Breadcrumb: Plano → Módulo → Capítulo
- Header: título, tempo estimado, badges de status
- Conteúdo markdown renderizado (usando `django-markdown-deux` ou filtro customizado)
- Barra lateral (desktop): índice do módulo (links para outros capítulos)
- Barra de progresso de leitura (JS: detecta quando scrollou até o fim)
- Botão "Concluí a leitura" (ativado após scroll completo)
- Navegação: "Capítulo anterior" / "Próximo capítulo"

### 6.5 `study_plan/chapter_note.html`

**Herda:** `base.html`

**Conteúdo:**
- Instruções sobre aprendizagem ativa (por que escrever com suas palavras)
- Textarea grande: "Explique com suas palavras o que aprendeu"
- Se já existe nota salva: exibe a anterior (modo edição)
- Botão "Salvar e continuar para a reflexão"

### 6.6 `study_plan/chapter_reflection.html`

**Herda:** `base.html`

**Conteúdo:**
- 3 textareas rotuladas:
  - "O que você entendeu neste capítulo?"
  - "Qual foi a parte mais importante?"
  - "Qual foi a parte mais difícil ou que gerou dúvida?"
- Se já existe reflexão: exibe os valores anteriores (modo edição)
- Botão "Salvar e ir para o mini quiz"

### 6.7 `study_plan/chapter_mini_quiz.html`

**Herda:** `base.html`

**Conteúdo:**
- Aviso: "3–5 questões do banco relacionadas ao tema que você estudou"
- Se não há questões suficientes no banco para o tema: mensagem amigável + link para treino geral
- Se há questões: botão "Iniciar mini quiz"
- Após clicar → redireciona para `/questoes/treino/<uuid>/` (view existente) com o Quiz recém-criado
- O resultado redireciona para `/questoes/resultado/<uuid>/` (view existente)
- Após o resultado: link "Voltar ao plano" + "Próximo capítulo"

### 6.8 `study_plan/error_notebook.html`

**Herda:** `base.html`

**Conteúdo:**
- Filtros: por disciplina, por status (revisada / pendente), por "erradas mais vezes"
- Lista de cards por questão errada:
  - Enunciado truncado, disciplina, alternativa dada, alternativa correta
  - Contador de erros, data do último erro, próxima revisão sugerida
  - Campo de anotação pessoal (HTMX: salva inline sem reload)
  - Botão "Revisar" (abre questão em modal ou nova tela)
  - Botão "Marcar como revisada"
- Paginação (20 itens por página)
- Estado vazio: "Nenhum erro registrado ainda — continue treinando!"

### 6.9 `study_plan/progress.html`

**Herda:** `base.html`

**Conteúdo:**
- Cards de métricas: streak atual, maior streak, dias estudados, capítulos concluídos, resumos escritos
- Calendário visual do mês (grid 7×5, célula verde = estudou, cinza = não estudou)
- Progresso por módulo (barras)
- Histórico de atividade (lista dos últimos 10 dias com capítulos estudados)

---

## 7. Integrações

### 7.1 Integração com o app `questions`

**Como:** `StudyChapter` tem um campo `related_subjects` (ManyToManyField → Subject). O `MiniQuizService` usa esse campo para selecionar questões do banco existente.

```
Usuária conclui capítulo "Raiva — Patologia e Transmissão"
  → chapter.related_subjects inclui Subject(slug="zoonoses-vigilancia")
  → MiniQuizService.create_mini_quiz(user, chapter):
      1. Busca question_ids via QuestionService.get_practice_questions(subject=..., quantity=5)
      2. Cria Quiz(quiz_type="mini", chapter=chapter, quantity=5)
      3. bulk_create QuizQuestion
      4. Retorna quiz.id
  → Redireciona para /questoes/treino/<uuid>/ (view existente, sem alteração)
```

**Fallback:** se `related_subjects` não tem questões suficientes (< 3), o sistema avisa e oferece o link para treino geral da disciplina em vez de criar um mini quiz vazio.

**Sugestão de questões após o capítulo:** o serviço também pode gerar um link direto para `FilterView` pré-preenchido com a disciplina do módulo (`?subject=<id>`), exibido na tela de conclusão do capítulo.

### 7.2 Integração com o app `exams`

**Quiz model:** adicionado campo `chapter` (FK nullable). O mini quiz é um Quiz normal com `quiz_type="mini"` e `chapter` preenchido.

**Resultado:** a tela de resultado (`ResultView`) existente já funciona. Após ver o resultado, o usuário vê o link "Voltar ao plano" — implementado via query param `?next=/plano/modulo/<slug>/` ou via `chapter_id` na sessão.

**ErrorNotebook:** ao finalizar qualquer Quiz (treino, simulado ou mini quiz), o `ErrorNotebookService.sync_errors(user, quiz)` percorre os `UserAnswer` do quiz, encontra os erros (`is_correct=False`) e faz upsert em `ErrorNotebookEntry` — incrementando `wrong_count`, atualizando `last_wrong_at` e calculando `next_review_at`.

Este service pode ser chamado ao final do `QuizService.submit_answers()` (sem alterar a assinatura pública) ou como signal `post_save` em `UserAnswer`.

### 7.3 Integração com o app `performance`

**Streak:** o `PerformanceService` existente calcula streak a partir de `StudySession`. O plano de estudos cria uma `StudySession` ao concluir um capítulo (se ainda não existe uma para o dia), garantindo que o dia seja contado no streak geral — **sem alterar a lógica do dashboard**.

**Dashboard principal:** poderá exibir um novo widget "Progresso do Plano" (% geral de conclusão) — mas isso é opcional e não bloqueia nenhuma das fases.

### 7.4 Integração com o app `dashboard`

**Navbar:** adicionar item "Plano de Estudos" com link para `/plano/`. A navbar está em `templates/base.html`. Esta é a única alteração no sistema atual de UI.

---

## 8. Plano de Implementação

### Fase 1 — Fundação (Módulos + Capítulos + Progresso)

**Objetivo:** o sistema consegue exibir os 14 módulos, seus capítulos e salvar progresso de leitura.

**Entregáveis:**
- Models: `StudyModule`, `StudyChapter`, `LessonProgress`
- Migration inicial do app `study_plan`
- Management command `import_study_plan`: lê os arquivos MASTER de `docs/` e popula `StudyModule` + `StudyChapter` (mesmo padrão do `import_questions`)
- Views: `PlanDashboardView`, `ModuleListView`, `ModuleDetailView`, `ChapterReadView`, `ChapterCompleteView`
- Templates: `dashboard.html`, `module_list.html`, `module_detail.html`, `chapter_read.html`
- Service: `PlanService` com métodos `get_next_chapter(user)`, `get_module_progress(user, module)`, `get_overall_progress(user)`
- Alteração em `base.html`: adicionar "Plano de Estudos" na navbar

**Dependências:** nenhuma dependência nova. Usa BaseModel, User e Subject existentes.

**Complexidade:** Média
- O management command é o ponto mais trabalhoso (parsing dos MASTER)
- Os MASTER não têm um formato 100% uniforme entre si — o parser precisará de adaptações por arquivo ou de um formato mínimo de marcação de seções
- As views são simples CRUD com `LoginRequiredMixin`

**Riscos:**
- **Parser dos MASTER:** os arquivos MASTER têm estrutura variável. Solução: usar cabeçalhos `##` como delimitadores de capítulo (padrão markdown) e `###` para subseções. Onde houver variação, configurar manualmente via `mapping.py` (mesmo padrão da Fase 3 do projeto).
- **Volume de conteúdo:** capítulos com muitos caracteres podem tornar a tela lenta. Solução: renderizar markdown no servidor via filtro Django, não no cliente.

**Critério de conclusão da Fase 1:**
Conseguir acessar `/plano/`, ver os 14 módulos, entrar em qualquer capítulo, ler o conteúdo e clicar "Concluí a leitura" — com progresso salvo no banco e refletido no dashboard do plano.

---

### Fase 2 — Aprendizagem Ativa e Reflexão

**Objetivo:** adicionar as etapas de escrita após a leitura de cada capítulo.

**Entregáveis:**
- Models: `ActiveLearningNote`, `GuidedReflection`
- Migration (Fase 2)
- Forms: `ActiveLearningNoteForm`, `GuidedReflectionForm`
- Views: `ChapterNoteView`, `ChapterReflectionView`
- Templates: `chapter_note.html`, `chapter_reflection.html`
- Service: `PlanService` extendido com `get_chapter_completion_status(user, chapter)` (retorna quais etapas foram concluídas: leitura, nota, reflexão, mini quiz)

**Dependências:** Fase 1 concluída.

**Complexidade:** Baixa
- Models simples (texto livre)
- Forms com validação básica (campo obrigatório, mínimo de caracteres)
- Views CBV com `FormView`

**Riscos:**
- **UX do fluxo em etapas:** o fluxo leitura → nota → reflexão → mini quiz exige que o usuário siga a sequência, mas não deve ser rígido demais (se ela precisar sair no meio e voltar, o sistema deve retomar de onde parou). Solução: `LessonProgress.status` já rastreia isso; as views verificam qual etapa está pendente e redirecionam.

**Critério de conclusão da Fase 2:**
Concluir um capítulo completo com leitura + nota + reflexão, ver as respostas salvas e poder editar a nota depois.

---

### Fase 3 — Mini Quiz, Caderno de Erros e Questões Sugeridas

**Objetivo:** fechar o ciclo de aprendizagem com prática imediata e centralizar os erros.

**Entregáveis:**
- Alteração no model `Quiz`: novo `quiz_type="mini"` e campo `chapter` (FK nullable) + migration
- Service: `MiniQuizService.create_mini_quiz(user, chapter)` + `MiniQuizService.get_suggested_questions(chapter)`
- Views: `ChapterMiniQuizView`
- Template: `chapter_mini_quiz.html`
- Model: `ErrorNotebookEntry`
- Service: `ErrorNotebookService.sync_errors(user, quiz)` + `ErrorNotebookService.get_notebook(user, filters)`
- Views: `ErrorNotebookView`, `ErrorNoteView`, `ErrorReviewView`
- Template: `error_notebook.html`
- Hook no `QuizService.submit_answers()` para disparar `sync_errors` após finalizar qualquer quiz

**Dependências:** Fase 1 concluída (mini quiz precisa de capítulos mapeados). Fase 2 não é pré-requisito.

**Complexidade:** Alta
- A alteração no `Quiz` model exige migration e testes de regressão no app `exams`
- O `MiniQuizService` precisa garantir que não há questões repetidas entre mini quizzes do mesmo capítulo
- O `ErrorNotebookService.sync_errors` precisa ser idempotente (rodar 2× sem duplicar)
- O caderno de erros tem filtros + paginação

**Riscos:**
- **Falta de questões no banco para o mini quiz:** muitos capítulos mapeiam para disciplinas que têm questões no banco, mas a granularidade (capítulo vs. tópico vs. disciplina inteira) pode não ser suficiente para garantir 3–5 questões relevantes. Solução: o `MiniQuizService` tenta questões por `Subject` (disciplina) quando não encontra por `Topic`. Se ainda insuficiente (< 3 questões), exibe mensagem amigável e pula o mini quiz.
- **Impacto no `QuizService.submit_answers`:** adicionar o hook de sincronização de erros pode aumentar o tempo de resposta do POST. Solução: manter o hook leve (apenas upsert com `update_or_create`); se necessário, mover para Celery task em fase futura.

**Critério de conclusão da Fase 3:**
Concluir um capítulo completo com mini quiz, ver o resultado, e encontrar os erros do mini quiz no caderno de erros. Erros de treinos e simulados anteriores também aparecem no caderno.

---

### Fase 4 — Streak do Plano, Progresso Visual e Polimento

**Objetivo:** completar a experiência com visualização de progresso e métricas de consistência.

**Entregáveis:**
- Views: `ProgressView`
- Template: `progress.html` (calendário visual + métricas do plano)
- `PlanService.get_streak(user)`: calcula streak específico do plano (dias com ≥ 1 capítulo concluído)
- `PlanService.get_calendar_activity(user, month)`: retorna dict de datas com atividade para o calendário
- Polimento de UX: animações de conclusão, mensagens de incentivo, badges
- Testes: unitários dos services + integração das views

**Dependências:** Fases 1, 2 e 3 concluídas.

**Complexidade:** Baixa
- `ProgressView` é uma view de leitura (sem forms)
- O calendário é gerado no servidor com Python `calendar` stdlib
- Streak do plano segue o mesmo padrão do streak existente no dashboard

**Riscos:** Baixo. Esta fase é de polimento; sem novos modelos ou alterações críticas.

**Critério de conclusão da Fase 4:**
A usuária pode ver um calendário do mês com dias estudados marcados, ver o streak atual do plano, e todas as métricas de progresso funcionando.

---

### Análise de Viabilidade: Áudio (Funcionalidade 10)

**Contexto:** a usuária poderia gravar um áudio explicando o conteúdo estudado em vez de (ou além de) escrever no campo de texto.

**Análise técnica:**

| Aspecto | Avaliação |
|---|---|
| **Gravação no browser** | Viável via `MediaRecorder API` (suportado em Chrome, Firefox, Edge, Safari 14.1+). Zero dependências externas para gravação. |
| **Armazenamento** | Problemático. Áudios de 1–3 min em WebM/Opus pesam ~0,5–2 MB cada. Para 100+ capítulos, o custo de armazenamento seria significativo. O Render (PaaS atual) não tem armazenamento persistente de arquivos — precisaria de AWS S3 ou similar. |
| **Reprodução** | Simples via tag `<audio>` HTML5. |
| **Impacto na arquitetura** | Exigiria: campo `audio_file` no model `ActiveLearningNote`, integração com boto3/S3, configuração de `django-storages`, e aumento de custo mensal de infraestrutura. |
| **Alternativa mais simples** | Campo de texto já captura o mesmo conteúdo cognitivo. O valor pedagógico do áudio (falar em voz alta) pode ser obtido sem persistência — "grave mentalmente e depois escreva". |

**Recomendação:** **não implementar na versão atual**. O custo de infraestrutura (S3 + django-storages + configuração de CORS) não é justificado pelo ganho pedagógico marginal. Se no futuro houver necessidade de áudio, a arquitetura suporta: basta adicionar `audio_file = FileField()` no `ActiveLearningNote` e configurar um storage backend. Nenhuma migration destrutiva seria necessária.

---

## 9. Impacto no Sistema Atual

### O que será reutilizado (zero alteração)

| Componente | Como é reutilizado |
|---|---|
| `BaseModel` (apps/core) | Todos os novos models herdam UUID + timestamps |
| `User` (apps/accounts) | FK em todos os novos models |
| `Subject`, `Question`, `Alternative` (apps/questions) | MiniQuizService consulta questões; StudyModule linka a Subject |
| `QuizQuestion`, `UserAnswer` (apps/exams) | Mini quiz usa as views e models de resultado existentes sem alteração |
| `QuizService.get_result()` (apps/exams) | Result view existente exibe resultado do mini quiz igual a qualquer quiz |
| `PerformanceService` (apps/performance) | Streak do dashboard continua funcionando normalmente |
| `DashboardService` (apps/dashboard) | Dashboard principal não é alterado |
| Todos os templates existentes | Apenas `base.html` recebe um novo item na navbar |
| Configurações Django (settings, URLs raiz) | Apenas `config/urls.py` recebe um novo `path("plano/", ...)` |

### O que será alterado (mudanças mínimas e seguras)

| Arquivo | Alteração | Impacto |
|---|---|---|
| `apps/exams/models.py` | Novo valor `MINI` em `TYPE_CHOICES` + campo `chapter` nullable | Migration segura; nenhum quiz existente é afetado |
| `apps/exams/services/quiz_service.py` | Hook ao final de `submit_answers()` para chamar `ErrorNotebookService` | Adição ao fim do método existente; não altera assinatura |
| `templates/base.html` | Novo `<li>` na navbar: "Plano de Estudos" | Puramente aditivo |
| `config/urls.py` | Novo `path("plano/", ...)` | Puramente aditivo |
| `config/settings/base.py` | `"apps.study_plan"` adicionado em `INSTALLED_APPS` | Puramente aditivo |

### O que será criado (novo)

| Tipo | Quantidade |
|---|---|
| Novo app Django | 1 (`apps/study_plan/`) |
| Novos models | 6 (`StudyModule`, `StudyChapter`, `LessonProgress`, `ActiveLearningNote`, `GuidedReflection`, `ErrorNotebookEntry`) |
| Novos services | 3 (`PlanService`, `MiniQuizService`, `ErrorNotebookService`) |
| Novas views | 11 |
| Novos templates | 9 |
| Novo management command | 1 (`import_study_plan`) |
| Novos forms | 3 |
| Novas migrations | 2 (1 nova para study_plan + 1 alteração em exams) |
| Novos URLs | 12 |

---

## 10. Estimativa Final

### Contagem de arquivos

| Categoria | Novos | Alterados |
|---|---|---|
| `apps/study_plan/__init__.py` | 1 | 0 |
| `apps/study_plan/apps.py` | 1 | 0 |
| `apps/study_plan/admin.py` | 1 | 0 |
| `apps/study_plan/models.py` | 1 | 0 |
| `apps/study_plan/forms.py` | 1 | 0 |
| `apps/study_plan/urls.py` | 1 | 0 |
| `apps/study_plan/views.py` | 1 | 0 |
| `apps/study_plan/migrations/0001_initial.py` | 1 | 0 |
| `apps/study_plan/services/plan_service.py` | 1 | 0 |
| `apps/study_plan/services/mini_quiz_service.py` | 1 | 0 |
| `apps/study_plan/services/error_notebook_service.py` | 1 | 0 |
| `apps/study_plan/services/__init__.py` | 1 | 0 |
| `apps/study_plan/management/commands/import_study_plan.py` | 1 | 0 |
| `apps/study_plan/management/__init__.py` + `commands/__init__.py` | 2 | 0 |
| `templates/study_plan/dashboard.html` | 1 | 0 |
| `templates/study_plan/module_list.html` | 1 | 0 |
| `templates/study_plan/module_detail.html` | 1 | 0 |
| `templates/study_plan/chapter_read.html` | 1 | 0 |
| `templates/study_plan/chapter_note.html` | 1 | 0 |
| `templates/study_plan/chapter_reflection.html` | 1 | 0 |
| `templates/study_plan/chapter_mini_quiz.html` | 1 | 0 |
| `templates/study_plan/error_notebook.html` | 1 | 0 |
| `templates/study_plan/progress.html` | 1 | 0 |
| `apps/exams/models.py` | 0 | 1 |
| `apps/exams/services/quiz_service.py` | 0 | 1 |
| `apps/exams/migrations/000X_add_mini_quiz.py` | 1 | 0 |
| `templates/base.html` | 0 | 1 |
| `config/urls.py` | 0 | 1 |
| `config/settings/base.py` | 0 | 1 |
| **TOTAL** | **27** | **5** |

### Complexidade geral

| Critério | Avaliação |
|---|---|
| **Risco arquitetural** | Baixo — novo app isolado, sem remodelar os existentes |
| **Risco de regressão** | Baixo — apenas 5 arquivos alterados, todos com mudanças aditivas |
| **Complexidade de parsing** | Média — `import_study_plan` exige cuidado com variações entre MASTER files |
| **Complexidade de UX** | Média — fluxo em etapas (leitura → nota → reflexão → mini quiz) exige gerenciamento de estado |
| **Complexidade de dados** | Baixa — todos os models são simples; o mais complexo é `ErrorNotebookEntry` |
| **Testabilidade** | Alta — services são Python puro, testáveis sem HTTP |

### Tempo estimado por fase

| Fase | Complexidade | Estimativa |
|---|---|---|
| Fase 1 — Fundação | Média | 2–3 dias |
| Fase 2 — Aprendizagem Ativa | Baixa | 1–2 dias |
| Fase 3 — Mini Quiz + Caderno de Erros | Alta | 3–4 dias |
| Fase 4 — Progresso Visual + Polimento | Baixa | 1 dia |
| **Total** | **Média-Alta** | **~7–10 dias de desenvolvimento** |

### Dependências externas

Nenhuma nova biblioteca Python é necessária para as Fases 1–4. O markdown dos capítulos pode ser renderizado com:
- **Opção A:** `django-markdown-deux` (simples, sem configuração) → adicionar ao `requirements/base.txt`
- **Opção B:** Filtro customizado com `mistune` ou `markdown` (já bem conhecidas no ecossistema Python)

Recomendação: **Opção A** (`django-markdown-deux`), por consistência com o padrão "less code" do projeto.

---

## Resumo Executivo

A funcionalidade "Plano de Estudos" adiciona um novo app Django (`study_plan`) com 6 models, 3 services, 11 views e 9 templates ao Nícia Track. Ela transforma os 14 arquivos MASTER em módulos e capítulos consultáveis no banco, entrega uma experiência guiada de estudo (leitura → nota → reflexão → mini quiz → prática), centraliza erros em um caderno próprio e rastreia consistência via streak.

A implementação reutiliza ao máximo o que existe: o mini quiz usa o `Quiz` model e as views de resultado existentes; o caderno de erros consome `UserAnswer` já salvo; o streak estende o `StudySession` existente. Apenas 5 arquivos são alterados — todos com mudanças aditivas e seguras.

O impacto no sistema atual em produção é mínimo e reversível: um novo item na navbar, um novo path de URL e uma migration nullable no model `Quiz`.

---

*Documento gerado em 2026-06-30 com base na análise completa de PROJECT_EXPLAINED.md, PLANO_DE_ESTUDOS_MASTER.md, todos os models.py, views.py e templates existentes.*
