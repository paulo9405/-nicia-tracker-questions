# Plano de Implementação — Fase 3: Mini Quiz, Caderno de Erros e Questões Sugeridas

**Data:** 2026-06-30  
**Status:** APROVADO — pronto para implementar  
**Baseline:** 158 testes passando  

---

## Visão Geral

A Fase 3 fecha o ciclo de aprendizagem ativo: após ler um capítulo e registrar reflexões (Fases 1 e 2), a candidata pratica com questões reais do banco e tem seus erros centralizados automaticamente.

Três entregáveis independentes mas integrados:

1. **Mini Quiz** — 3 a 5 questões do banco após concluir um capítulo
2. **Caderno de Erros** (`ErrorNotebookEntry`) — centraliza questões erradas de qualquer quiz
3. **Questões Sugeridas** — link de prática rápida relacionada ao capítulo estudado

---

## 1. Models

### 1.1 `ErrorNotebookEntry` (novo, em `apps/study_plan/models.py`)

```python
class ErrorNotebookEntry(BaseModel):
    user = FK(User, CASCADE, related_name="error_notebook_entries")
    question = FK(Question, PROTECT, related_name="error_notebook_entries")
    last_user_answer = FK(UserAnswer, SET_NULL, null=True, blank=True)
    wrong_count = PositiveSmallIntegerField(default=1)
    last_wrong_at = DateTimeField()
    next_review_at = DateField(null=True, blank=True)
    personal_note = TextField(blank=True)
    is_reviewed = BooleanField(default=False)

    class Meta:
        unique_together = [("user", "question")]
        indexes:
          - (user, next_review_at)
          - (user, wrong_count)
          - (user, is_reviewed)
```

**Lógica de `next_review_at`** (calculada no service):
- wrong_count == 1 → D+1
- wrong_count == 2 → D+3
- wrong_count == 3 → D+7
- wrong_count >= 4 → D+14

### 1.2 Alteração no model `Quiz` (em `apps/exams/models.py`)

```python
# Adicionar ao Quiz:
MINI = "mini"
TYPE_CHOICES += [(MINI, "Mini Quiz")]
chapter = FK(StudyChapter, SET_NULL, null=True, blank=True, related_name="mini_quizzes")
```

Migration segura: FK nullable, nenhum dado existente é afetado.

---

## 2. Services

### 2.1 `MiniQuizService` (novo, em `apps/study_plan/services/mini_quiz_service.py`)

**Método principal: `create_mini_quiz(user, chapter) -> Quiz | None`**

Estratégia de seleção de questões (prioridade decrescente):

1. **Por Topic:** busca Topics cujo nome contenha alguma das tags do capítulo (`chapter.tags`). Se encontrar questões suficientes (≥ 3), usa.
2. **Por Subject (via module.subject):** se o capítulo tem `chapter.module.subject`, usa `QuestionService.get_practice_questions(subject_id=..., topic_id=None, quantity=5)`.
3. **Por related_subjects:** itera pelos subjects em `chapter.related_subjects.all()` até ter ≥ 3 questões.
4. **Fallback:** retorna `None` — sem questões suficientes, não cria quiz vazio.

Se encontrou questões suficientes:
- Cria `Quiz(user=user, quiz_type=Quiz.MINI, chapter=chapter, quantity=N, status=IN_PROGRESS)`
- `bulk_create` de `QuizQuestion`
- Retorna o quiz

**Método auxiliar: `get_suggested_questions(chapter, limit=5) -> QuerySet`**

- Mesmo algoritmo de busca, mas retorna QuerySet em vez de criar Quiz
- Usado para o card de "Questões Sugeridas" na tela de conclusão do capítulo

**Método auxiliar: `count_available_questions(chapter) -> int`**

- Conta quantas questões existem para o capítulo sem criar quiz
- Usado para mostrar "X questões disponíveis" na tela do mini quiz

### 2.2 `ErrorNotebookService` (novo, em `apps/study_plan/services/error_notebook_service.py`)

**Método principal: `sync_errors(user, quiz) -> int`**

Idempotente (rodar 2× com o mesmo quiz → mesmo resultado):

```
1. Busca todos os UserAnswer do quiz onde is_correct=False e selected_alternative is not None
   (puladas não vão para o caderno — não foi tentativa de resposta)
2. Para cada UserAnswer errado:
   a. update_or_create em ErrorNotebookEntry:
      - Existe → incrementa wrong_count, atualiza last_wrong_at e last_user_answer
      - Não existe → cria com wrong_count=1
   b. Calcula next_review_at baseado no novo wrong_count
3. Retorna quantidade de entradas criadas/atualizadas
```

**Método: `get_notebook(user, subject_id=None, is_reviewed=None, order_by="-wrong_count") -> QuerySet`**

- Filtro opcional por disciplina e status de revisão
- Ordenação configurável
- `select_related("question__subject", "last_user_answer")`

**Método: `save_personal_note(user, entry_id, note) -> ErrorNotebookEntry`**

- Salva anotação pessoal em uma entrada do caderno
- `update_or_create` por `(user, id)`

**Método: `mark_as_reviewed(user, entry_id) -> ErrorNotebookEntry`**

- Define `is_reviewed=True`, `next_review_at=None`
- Não remove do caderno — só muda status

---

## 3. Views

### 3.1 `ChapterMiniQuizView` (em `apps/study_plan/views.py`)

- **GET `/plano/capitulo/<slug>/mini-quiz/`**: exibe tela com informações sobre o mini quiz
  - Se `MiniQuizService.count_available_questions(chapter) < 3`: exibe mensagem amigável com link para treino geral da disciplina
  - Se há questões: exibe botão "Iniciar Mini Quiz" + card com questões sugeridas
  - Se quiz já existe para este capítulo (quiz não finalizado): redireciona para o quiz em andamento
- **POST**: chama `MiniQuizService.create_mini_quiz(user, chapter)` e redireciona para `/questoes/treino/<uuid>/`

### 3.2 `ErrorNotebookView` (em `apps/study_plan/views.py`)

- **GET `/plano/caderno-de-erros/`**: lista paginada (20 itens) de `ErrorNotebookEntry`
- Filtros via GET params: `subject`, `is_reviewed` (`0`/`1`), `order` (`-wrong_count`, `-last_wrong_at`)
- Contexto: lista de subjects para o filtro, contagem total por status

### 3.3 `ErrorNoteView` (em `apps/study_plan/views.py`)

- **POST `/plano/caderno-de-erros/<uuid>/nota/`**: salva `personal_note` via `ErrorNotebookService.save_personal_note()`
- Retorna redirect para `error_notebook` com âncora na entrada

### 3.4 `ErrorReviewView` (em `apps/study_plan/views.py`)

- **POST `/plano/caderno-de-erros/<uuid>/revisar/`**: chama `ErrorNotebookService.mark_as_reviewed()`
- Retorna redirect para `error_notebook`

---

## 4. Templates

### 4.1 `study_plan/chapter_mini_quiz.html`

- Herda `base.html`
- Breadcrumb: Plano → Módulo → Capítulo → Mini Quiz
- Header: título do capítulo, tema, questões disponíveis
- **Estado: questões insuficientes:** card de aviso + link para treino geral da disciplina
- **Estado: questões disponíveis:** card com N questões disponíveis + botão "Iniciar Mini Quiz"
- Card "Questões sugeridas" (lista de até 5 questões com enunciado truncado)
- Link "Pular e ir ao próximo capítulo"

### 4.2 `study_plan/error_notebook.html`

- Herda `base.html`
- Filtros no topo: select de disciplina, toggle revisada/pendente, ordenação
- Lista de cards por entrada:
  - Enunciado truncado (150 chars), disciplina (badge)
  - Número de erros (badge), data do último erro, próxima revisão
  - Alternativa escolhida ✗ vs alternativa correta ✓ (se `last_user_answer` disponível)
  - Textarea de anotação pessoal com botão "Salvar nota" (form POST)
  - Botão "Marcar como revisada" (form POST)
- Paginação Bootstrap (20 por página)
- Estado vazio: mensagem motivacional

---

## 5. Integração com Quiz existente

### 5.1 Hook em `QuizService.submit_answers()`

Após a linha `quiz.save(update_fields=["status", "finished_at"])`, adicionar:

```python
from apps.study_plan.services.error_notebook_service import ErrorNotebookService
ErrorNotebookService.sync_errors(quiz.user, quiz)
```

Esse hook é chamado para todos os tipos de quiz (treino, simulado, mini quiz). Não altera a assinatura do método.

**Risco:** aumenta o tempo de resposta do POST de `submit_answers`. Mitigação: o `sync_errors` faz apenas um `filter` + N `update_or_create` — custo O(questões_erradas), geralmente < 5 operações.

### 5.2 Redirecionamento após Mini Quiz

O mini quiz usa as views existentes do app `exams`:
- Play: `/questoes/treino/<uuid>/`  
- Resultado: `/questoes/resultado/<uuid>/`

Após o resultado, o link "Voltar ao plano" é gerado via `quiz.chapter_id` (FK que adicionamos). Na `ResultView` do app exams, nenhuma alteração é necessária — o link é gerado no template via `quiz.chapter`.

---

## 6. Migrações

### 6.1 Migration no app `study_plan` (`0003_errornotebookentry.py`)

Cria a tabela `study_plan_errornotebookentry` com todos os campos e índices.

### 6.2 Migration no app `exams` (`0002_quiz_add_mini_type_and_chapter.py`)

Altera o model `Quiz`:
- Adiciona `MINI` em `quiz_type` choices (apenas alteração de choices, sem DDL)
- Adiciona coluna `chapter_id` (FK nullable para `study_plan_studychapter`)

**Ordem de aplicação:** `study_plan.0002` deve existir antes de `exams.0002` (a FK de Quiz→StudyChapter depende da tabela já existir). Garantido via `dependencies` na migration.

---

## 7. Estratégia de Fallback de Questões

```
Capítulo "Raiva — Patologia e Transmissão"
  chapter.tags = ["raiva", "vírus-da-raiva", "profilaxia-raiva"]
  chapter.module.subject = Subject(slug="zoonoses-vigilancia")
  chapter.related_subjects = [Subject(slug="zoonoses-vigilancia")]

MiniQuizService.create_mini_quiz(user, chapter):

  1. Tenta por Topic:
     → Topics onde name ilike qualquer tag → ex.: Topic("Raiva")
     → QuestionService.get_practice_questions(subject_id=..., topic_id=topic.id, quantity=5)
     → Encontrou 8 questões → usa 5 → OK ✓

  2. Se step 1 < 3 questões:
     → Tenta por module.subject: Subject("Zoonoses e Vigilância")
     → get_practice_questions(subject_id=..., topic_id=None, quantity=5)
     → Encontrou 50 questões → usa 5 → OK ✓

  3. Se step 2 < 3 questões:
     → Itera related_subjects, acumula question_ids
     → Encontrou N → usa min(N, 5) → OK se N >= 3 ✓

  4. Se tudo < 3:
     → Retorna None → view exibe mensagem "questões insuficientes"
```

---

## 8. Impacto no Sistema Existente

### Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `apps/exams/models.py` | +`MINI` em `TYPE_CHOICES`; +campo `chapter` nullable |
| `apps/exams/services/quiz_service.py` | +hook `sync_errors` ao final de `submit_answers()` |
| `apps/study_plan/models.py` | +model `ErrorNotebookEntry` |
| `apps/study_plan/views.py` | +`ChapterMiniQuizView`, `ErrorNotebookView`, `ErrorNoteView`, `ErrorReviewView` |
| `apps/study_plan/urls.py` | +4 rotas |
| `apps/study_plan/admin.py` | +`ErrorNotebookEntryAdmin` |
| `templates/study_plan/chapter_reflection.html` | Redirect após salvar vai para `chapter_mini_quiz` em vez de `chapter_read` |
| `config/urls.py` | Já inclui `/plano/` — sem alteração |

### Arquivos criados

| Arquivo | Conteúdo |
|---|---|
| `apps/study_plan/services/mini_quiz_service.py` | `MiniQuizService` |
| `apps/study_plan/services/error_notebook_service.py` | `ErrorNotebookService` |
| `apps/study_plan/migrations/0003_errornotebookentry.py` | Migration gerada |
| `apps/exams/migrations/0002_quiz_chapter.py` | Migration gerada |
| `templates/study_plan/chapter_mini_quiz.html` | Template do mini quiz |
| `templates/study_plan/error_notebook.html` | Template do caderno de erros |
| `tests/unit/test_mini_quiz_service.py` | Testes unitários do MiniQuizService |
| `tests/unit/test_error_notebook_service.py` | Testes unitários do ErrorNotebookService |
| `tests/integration/test_phase3_views.py` | Testes de integração das novas views |

---

## 9. Testes Planejados

### Unitários — `MiniQuizService` (≥ 5 testes)

1. `test_create_mini_quiz_por_topic` — encontra questões via tag → cria quiz com quiz_type=MINI
2. `test_create_mini_quiz_fallback_subject` — sem topic match → cria quiz via subject
3. `test_create_mini_quiz_retorna_none_sem_questoes` — 0 questões disponíveis → retorna None
4. `test_mini_quiz_nao_repete_questoes_ja_respondidas` — se user já respondeu X questões do capítulo, não repete
5. `test_count_available_questions` — conta corretamente

### Unitários — `ErrorNotebookService` (≥ 5 testes)

1. `test_sync_errors_cria_entrada_novo_erro` — quiz com 2 erros → cria 2 entradas
2. `test_sync_errors_incrementa_wrong_count` — quiz com erro já no caderno → wrong_count aumenta
3. `test_sync_errors_puladas_nao_vao_para_caderno` — questão pulada não cria entrada
4. `test_sync_errors_idempotente` — rodar 2× → mesmo resultado
5. `test_next_review_at_logica` — wrong_count 1→D+1, 2→D+3, 3→D+7, 4→D+14
6. `test_mark_as_reviewed` — entry.is_reviewed=True após chamar método

### Integração — Views (≥ 6 testes)

1. `test_chapter_mini_quiz_get_sem_questoes` — exibe mensagem de questões insuficientes
2. `test_chapter_mini_quiz_get_com_questoes` — exibe botão de iniciar
3. `test_chapter_mini_quiz_post_cria_quiz` — POST cria Quiz e redireciona para play
4. `test_error_notebook_get_vazio` — lista vazia exibe estado vazio
5. `test_error_notebook_get_com_entradas` — lista mostra entradas
6. `test_error_review_post_marca_como_revisada` — POST chama mark_as_reviewed

---

## 10. Ordem de Implementação

1. Model `ErrorNotebookEntry` + migration (`study_plan/0003`)
2. Alteração no model `Quiz` + migration (`exams/0002`)
3. `ErrorNotebookService` (sem dependência de views)
4. Hook em `QuizService.submit_answers()`
5. `MiniQuizService` (depende de Quiz.MINI estar definido)
6. Views e URLs
7. Templates
8. Testes (unitários → integração)
9. Alteração no redirect da `ChapterReflectionView` (→ `chapter_mini_quiz`)
10. Atualização de `PROJECT_EXPLAINED.md` e criação de `PHASE_3_IMPLEMENTATION.md`

---

## 11. Restrições Respeitadas

- ❌ Não implementar: Calendário, Revisão Espaçada completa, Áudio, Notificações, Gamificação
- ✅ Mini quiz reutiliza Quiz + QuizQuestion + UserAnswer existentes
- ✅ Resultado do mini quiz usa `ResultView` existente (sem alteração)
- ✅ `ErrorNotebookService.sync_errors` é idempotente
- ✅ FK `Quiz.chapter` é nullable → migration segura

---

*Plano gerado em 2026-06-30 com base em análise completa dos models, services, views e templates existentes.*
