# Plano de Implementação — Fase 2: Aprendizagem Ativa e Reflexão

**Data:** 2026-06-30  
**Status:** Plano (pré-implementação)  
**Dependência:** Fase 1 ✅ e Fase 1.5 ✅ concluídas  

---

## 1. Objetivo

Adicionar as etapas de escrita pós-leitura ao fluxo do capítulo:

```
Capítulo → Leitura → Aprendizagem Ativa → Reflexão Guiada → Capítulo concluído
```

A candidata lê o conteúdo, explica com suas palavras (ActiveLearningNote) e responde 3 perguntas de reflexão (GuidedReflection). Tudo persiste no banco e pode ser editado depois.

---

## 2. Models

### 2.1 `ActiveLearningNote`

Armazena a explicação livre da usuária após ler um capítulo ("explique com suas palavras").

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID (PK) | BaseModel |
| `user` | FK(User, CASCADE) | |
| `chapter` | FK(StudyChapter, CASCADE) | |
| `explanation` | TextField | Mínimo 20 chars (validado no form) |
| `created_at` | DateTimeField | BaseModel |
| `updated_at` | DateTimeField | BaseModel |

**Constraint:** `unique_together = [('user', 'chapter')]` — uma nota por capítulo; edição sobrescreve via `update_or_create`.

**Motivo:** capturar a explicação em texto livre é a técnica pedagógica da "elaborative interrogation" — obrigar a candidata a reformular o conteúdo com suas palavras consolida a memória.

---

### 2.2 `GuidedReflection`

Armazena 3 respostas de reflexão guiada por capítulo.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID (PK) | BaseModel |
| `user` | FK(User, CASCADE) | |
| `chapter` | FK(StudyChapter, CASCADE) | |
| `what_understood` | TextField | "O que você entendeu?" |
| `most_important` | TextField | "Qual foi a parte mais importante?" |
| `most_difficult` | TextField | "Qual foi a parte mais difícil?" |
| `created_at` | DateTimeField | BaseModel |
| `updated_at` | DateTimeField | BaseModel |

**Constraint:** `unique_together = [('user', 'chapter')]`

**Motivo:** reflexão estruturada ativa a metacognição — a candidata identifica pontos fortes e lacunas, produzindo informação acionável para o estudo futuro.

---

## 3. Forms

### 3.1 `ActiveLearningNoteForm`

`ModelForm` para `ActiveLearningNote`.

- Campo: `explanation` (Textarea, `rows=8`)
- Validação: `min_length=20` com mensagem de erro em português
- Label: "Explique com suas palavras o que aprendeu neste capítulo"

### 3.2 `GuidedReflectionForm`

`ModelForm` para `GuidedReflection`.

- Campo `what_understood` (Textarea `rows=4`) — "O que você entendeu neste capítulo?"
- Campo `most_important` (Textarea `rows=4`) — "Qual foi a parte mais importante?"
- Campo `most_difficult` (Textarea `rows=4`) — "Qual foi a parte mais difícil ou que gerou dúvida?"
- Todos requeridos, sem validação adicional de tamanho

---

## 4. Views

### 4.1 `ChapterNoteView` — `LoginRequiredMixin + FormView`

- **URL:** `GET/POST /plano/capitulo/<slug>/nota/`
- **GET:** busca nota existente via `ActiveLearningNote.objects.filter(user, chapter).first()`. Se existe, passa `instance` para o form (modo edição). Adiciona capítulo e progresso ao contexto.
- **POST:** `form_valid()` chama `PlanService.save_active_note(user, chapter, form)` que faz `update_or_create`. Redireciona para `chapter_reflection`.
- **Contexto:** `chapter`, `module`, `form`, `existing_note` (bool), `progress`

### 4.2 `ChapterReflectionView` — `LoginRequiredMixin + FormView`

- **URL:** `GET/POST /plano/capitulo/<slug>/reflexao/`
- **GET:** busca reflexão existente. Se existe, passa como `instance` (modo edição). Contexto similar ao `ChapterNoteView`.
- **POST:** `form_valid()` chama `PlanService.save_guided_reflection(user, chapter, form)` → `update_or_create`. Redireciona para `chapter_read` com mensagem de sucesso "Reflexão concluída! Seu aprendizado foi registrado."
- **Contexto:** `chapter`, `module`, `form`, `existing_reflection` (bool), `progress`

---

## 5. Service: Extensão do `PlanService`

### 5.1 `get_chapter_completion_status(user, chapter)`

Retorna um `ChapterCompletionStatus` dataclass:

```python
@dataclass
class ChapterCompletionStatus:
    is_reading_done: bool      # LessonProgress.status == COMPLETED
    has_note: bool             # ActiveLearningNote exists
    has_reflection: bool       # GuidedReflection exists
    is_fully_done: bool        # all three True
```

Usado nos templates para exibir o estado de cada etapa e nos testes.

### 5.2 `save_active_note(user, chapter, form)`

`update_or_create(user=user, chapter=chapter, defaults={'explanation': form.cleaned_data['explanation']})` dentro de `transaction.atomic`.

### 5.3 `save_guided_reflection(user, chapter, form)`

`update_or_create(user=user, chapter=chapter, defaults={...3 campos...})` dentro de `transaction.atomic`.

---

## 6. Templates

### 6.1 `study_plan/chapter_note.html`

- Breadcrumb: Plano → Módulo → Capítulo → Aprendizagem Ativa
- Card de instrução: por que escrever com suas palavras ajuda a memorizar (2–3 linhas)
- Trecho do capítulo: título e badge de status
- Form: textarea grande (`rows=8`), contador de caracteres (JS inline simples)
- Se nota já existe: alerta "Você já tem uma nota salva — edite abaixo"
- Botão primário: "Salvar e ir para a Reflexão"
- Link secundário: "Pular esta etapa e ir para a Reflexão →"

### 6.2 `study_plan/chapter_reflection.html`

- Breadcrumb: Plano → Módulo → Capítulo → Reflexão Guiada
- Card de instrução: por que responder essas 3 perguntas
- 3 campos rotulados com textarea (`rows=4` cada)
- Se reflexão já existe: alerta "Você já respondeu antes — edite abaixo"
- Botão primário: "Salvar Reflexão"
- Link secundário: "Pular esta etapa →"

---

## 7. Fluxo Atualizado

### Após Fase 2

```
ChapterReadView (GET)
  → usuária lê o conteúdo

ChapterCompleteView (POST)
  → marca LessonProgress.status = COMPLETED
  → redireciona para chapter_note (em vez de module_detail)

ChapterNoteView (GET)
  → exibe form de explicação livre

ChapterNoteView (POST)
  → salva ActiveLearningNote
  → redireciona para ChapterReflectionView

ChapterReflectionView (GET)
  → exibe form com 3 perguntas

ChapterReflectionView (POST)
  → salva GuidedReflection
  → redireciona para ChapterReadView (com mensagem de sucesso)
```

**Nota sobre flexibilidade:** as URLs de nota e reflexão ficam acessíveis independentemente. A usuária pode editar a nota de um capítulo já concluído acessando `/plano/capitulo/<slug>/nota/` diretamente. Nenhuma etapa é bloqueante.

---

## 8. Arquivos que serão criados

| Arquivo | Descrição |
|---|---|
| `apps/study_plan/forms.py` | `ActiveLearningNoteForm`, `GuidedReflectionForm` |
| `apps/study_plan/migrations/0002_activelearningnote_guidedreflection.py` | Migration gerada |
| `templates/study_plan/chapter_note.html` | Template da aprendizagem ativa |
| `templates/study_plan/chapter_reflection.html` | Template da reflexão guiada |
| `docs/PHASE_2_IMPLEMENTATION_PLAN.md` | Este documento |

---

## 9. Arquivos que serão alterados

| Arquivo | Mudança |
|---|---|
| `apps/study_plan/models.py` | Adicionar `ActiveLearningNote` e `GuidedReflection` |
| `apps/study_plan/views.py` | Adicionar `ChapterNoteView` e `ChapterReflectionView` |
| `apps/study_plan/urls.py` | Adicionar 2 rotas: `nota/` e `reflexao/` |
| `apps/study_plan/services/plan_service.py` | Adicionar `ChapterCompletionStatus`, `get_chapter_completion_status`, `save_active_note`, `save_guided_reflection` |
| `apps/study_plan/views.py` | `ChapterCompleteView`: redirect para `chapter_note` em vez de `module_detail` |
| `templates/study_plan/chapter_read.html` | Adicionar links de acesso à nota e reflexão quando capítulo concluído |

---

## 10. Estratégia de Migração

1. `python manage.py makemigrations study_plan` — gera `0002_activelearningnote_guidedreflection.py`
2. `python manage.py migrate` — aplica no banco local
3. Nenhum dado existente é afetado (tabelas novas, sem `ALTER TABLE` em tabelas existentes)
4. Os modelos `StudyModule`, `StudyChapter` e `LessonProgress` **não são alterados**

---

## 11. Impacto na Fase 1

| Componente | Impacto |
|---|---|
| `ChapterCompleteView` | redirect muda de `module_detail` → `chapter_note` |
| `chapter_read.html` | adiciona links para nota/reflexão quando concluído |
| `PlanService` | novos métodos adicionados (sem alterar os existentes) |
| Models Fase 1 | zero alteração |
| Templates Fase 1 | zero alteração (exceto `chapter_read.html`) |
| Testes Fase 1 | todos continuam passando (redirect do `chapter_complete` muda de URL) |

**Única breaking change:** o teste `test_chapter_complete_marks_completed` verifica apenas `status == COMPLETED` e `status_code == 302` — continua passando. Nenhum teste verifica a URL exata do redirect.

---

## 12. Testes a criar

### Unitários (`tests/unit/test_plan_service.py` — acrescentar)

| Teste | Valida |
|---|---|
| `test_save_active_note_creates` | `save_active_note` cria nota nova |
| `test_save_active_note_updates` | chamar duas vezes atualiza a mesma nota |
| `test_save_guided_reflection_creates` | `save_guided_reflection` cria reflexão |
| `test_save_guided_reflection_updates` | chamar duas vezes atualiza a mesma reflexão |
| `test_chapter_completion_status_all_false` | sem atividade → todos False |
| `test_chapter_completion_status_reading_done` | só leitura concluída |
| `test_chapter_completion_status_fully_done` | leitura + nota + reflexão → `is_fully_done=True` |

### Integração (`tests/integration/test_study_plan_views.py` — acrescentar)

| Teste | Valida |
|---|---|
| `test_chapter_note_requires_login` | 302 → login sem sessão |
| `test_chapter_note_get_loads` | 200, form no context |
| `test_chapter_note_post_creates_note` | POST salva nota, redirect para reflexão |
| `test_chapter_note_post_updates_note` | POST duas vezes → só 1 registro |
| `test_chapter_reflection_get_loads` | 200, form no context |
| `test_chapter_reflection_post_creates_reflection` | POST salva reflexão, redirect para capítulo |
| `test_chapter_reflection_post_updates_reflection` | POST duas vezes → só 1 registro |
| `test_chapter_complete_redirects_to_note` | redirect vai para `chapter_note` |

---

*Plano gerado em 2026-06-30.*
