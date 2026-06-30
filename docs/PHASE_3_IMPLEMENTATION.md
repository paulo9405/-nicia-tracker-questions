# Relatório de Implementação — Fase 3: Mini Quiz, Caderno de Erros e Questões Sugeridas

**Data:** 2026-06-30  
**Status:** ✅ Concluída — 186 testes passando (0 falhas)  
**Versão anterior:** 158 testes  
**Novos testes:** +28 (16 unitários + 12 integração)

---

## Arquivos criados

| Arquivo | Linhas | Descrição |
|---|---|---|
| `apps/study_plan/services/mini_quiz_service.py` | ~90 | `MiniQuizService` com fallback em 3 níveis |
| `apps/study_plan/services/error_notebook_service.py` | ~80 | `ErrorNotebookService`: sync, filtros, notas, revisão |
| `apps/study_plan/migrations/0003_errornotebookentry.py` | ~70 | Migration gerada automaticamente |
| `apps/exams/migrations/0002_errornotebookentry.py` | ~60 | Migration: `Quiz.MINI` + `Quiz.chapter` |
| `templates/study_plan/chapter_mini_quiz.html` | ~90 | Template do mini quiz (2 estados) |
| `templates/study_plan/error_notebook.html` | ~120 | Template do caderno de erros |
| `tests/unit/test_mini_quiz_service.py` | ~155 | 7 testes unitários |
| `tests/unit/test_error_notebook_service.py` | ~175 | 9 testes unitários |
| `tests/integration/test_phase3_views.py` | ~255 | 12 testes de integração |
| `docs/PHASE_3_IMPLEMENTATION_PLAN.md` | ~280 | Plano pré-código |
| `docs/PHASE_3_IMPLEMENTATION.md` | — | Este documento |

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `apps/study_plan/models.py` | +`ErrorNotebookEntry` (model completo + helper `_next_review_date`) |
| `apps/exams/models.py` | +`MINI` em `TYPE_CHOICES`; +campo `chapter` (FK nullable para `StudyChapter`) |
| `apps/exams/services/quiz_service.py` | +hook `ErrorNotebookService.sync_errors()` ao final de `submit_answers()` |
| `apps/study_plan/views.py` | +4 views: `ChapterMiniQuizView`, `ErrorNotebookView`, `ErrorNoteView`, `ErrorReviewView`; redirect de `ChapterReflectionView` → `chapter_mini_quiz` |
| `apps/study_plan/urls.py` | +4 rotas: `mini-quiz/`, `caderno-de-erros/`, `/nota/`, `/revisar/` |
| `apps/study_plan/admin.py` | +`ErrorNotebookEntryAdmin` |
| `templates/base.html` | +link "Caderno de Erros" na navbar |
| `docs/PROJECT_EXPLAINED.md` | +seção "Fase 3 do Plano de Estudos" ao final |

---

## Decisões tomadas

### 1. Fallback em 3 níveis no MiniQuizService

O banco de questões não tem granularidade uniforme — há tópicos para algumas disciplinas, mas não para todas. Implementar apenas "por tópico" travaria o mini quiz para muitos capítulos.

A sequência de fallback:
1. **Topic matching tags** — mais preciso (ex.: "Raiva" match em tag "raiva")
2. **Subject do módulo** — disciplina inteira
3. **related_subjects** — disciplinas vinculadas ao capítulo

Se nenhum nível retorna ≥ 3 questões → retorna `None` → view exibe mensagem amigável.

### 2. Hook inline no submit_answers (não signal)

`sync_errors` é chamado diretamente no `submit_answers()` logo após o `quiz.save()`. Alternativas consideradas:

- **Signal `post_save` em `Quiz`:** menos explícito, difícil de rastrear, complicaria testes.
- **Celery task:** excessivo para operações O(pequeno) sem necessidade de assincronismo.
- **Hook inline:** simples, explícito, testável, zero dependências novas.

### 3. Questões puladas excluídas do caderno

`selected_alternative=None` = questão pulada = não foi tentativa de resposta. Registrar como erro distorceria métricas. A candidata deve ver no caderno apenas o que **errou**, não o que pulou por qualquer razão.

### 4. Idempotência via `get_or_create` + upsert manual

Django não tem um `upsert_with_increment` nativo. A solução:
```python
entry, created = ErrorNotebookEntry.objects.get_or_create(...)
if not created:
    entry.wrong_count += 1
    entry.save(update_fields=[...])
```
A unicidade é garantida pelo `unique_together(user, question)` no banco. Rodar `sync_errors` duas vezes com o mesmo quiz incrementa `wrong_count` (comportamento esperado — o usuário errou mais uma vez).

### 5. `Quiz.chapter` com `SET_NULL` (não PROTECT, não CASCADE)

- **CASCADE**: apagar capítulo apagaria histórico de quiz → inaceitável.
- **PROTECT**: impediria desativar um capítulo se houvesse mini quiz — rígido demais.
- **SET_NULL**: o quiz fica com `chapter=None`, preservando respostas e erros.

---

## Problemas encontrados

### 1. Campo `text` em vez de `statement`

Os testes foram escritos com `statement=...` mas o model `Question` usa `text=...`. Corrigido nos 3 arquivos de teste via sed.

### 2. `pytest-django` não instalado no ambiente

O ambiente local não tinha `pytest-django` instalado, causando falha de coleta. Instalado com `pip3 install --user pytest-django`. Também havia conflito com um pacote `decouple` errado (versão 0.0.7 sem `config`) — resolvido reinstalando `python-decouple`.

---

## Resultado da suíte de testes

```
186 passed, 0 failed, 83 warnings in 4.17s
```

Os 83 warnings são todos `UserWarning: No directory at: .../staticfiles/` — pré-existentes, irrelevantes.

---

## Estatísticas

| Métrica | Valor |
|---|---|
| Testes anteriores | 158 |
| Novos testes unitários | +16 (MiniQuizService: 7, ErrorNotebookService: 9) |
| Novos testes integração | +12 (Phase3Views) |
| **Total** | **186 passando, 0 falhas** |
| Models novos | 1 (`ErrorNotebookEntry`) |
| Models alterados | 1 (`Quiz`: +MINI + chapter) |
| Services novos | 2 |
| Views novas | 4 |
| Templates novos | 2 |
| URLs novas | 4 |
| Migrations novas | 2 |

---

## Próximos passos (Fase 4)

### Fase 4 — Streak do Plano, Progresso Visual e Polimento

- View: `ProgressView`
- Template: `progress.html` (calendário visual + métricas)
- `PlanService.get_streak(user)`: streak do plano (dias com ≥1 capítulo concluído)
- `PlanService.get_calendar_activity(user, month)`: dict data → contagem
- Polimento de UX: animações de conclusão, mensagens de incentivo
- Testes: unitários + integração

**Dependências:** Fases 1, 2 e 3 concluídas.  
**Complexidade:** Baixa — apenas view de leitura, calendário gerado com stdlib `calendar`.
