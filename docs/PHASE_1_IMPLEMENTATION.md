# Relatório de Implementação — Fase 1: Plano de Estudos

**Data:** 30/06/2026  
**Status:** ✅ Concluída — 141 testes passando (0 falhas)  
**Versão anterior:** 122 testes  
**Novos testes:** +19 (10 unitários + 9 integração)

---

## Arquivos criados

### App `apps/study_plan/`

| Arquivo | Linhas | Descrição |
|---|---|---|
| `__init__.py` | 0 | Pacote Python |
| `apps.py` | 8 | `StudyPlanConfig` |
| `models.py` | 142 | `StudyModule`, `StudyChapter`, `LessonProgress` |
| `admin.py` | ~50 | Admin com inline e filtros |
| `urls.py` | 13 | 5 rotas com namespace `study_plan` |
| `views.py` | 97 | 5 views (4 `TemplateView` + 1 `View`) |
| `services/__init__.py` | 0 | Pacote vazio |
| `services/plan_service.py` | 199 | `PlanService` + 2 dataclasses |
| `migrations/0001_initial.py` | ~100 | Migração gerada automaticamente |
| `management/__init__.py` | 0 | Pacote |
| `management/commands/__init__.py` | 0 | Pacote |
| `management/commands/import_study_plan.py` | ~350 | Command com 14 módulos e 98 capítulos |

### Templates `templates/study_plan/`

| Arquivo | Descrição |
|---|---|
| `dashboard.html` | Dashboard com métricas e CTA próximo capítulo |
| `module_list.html` | Lista de módulos (específicos/básicos) com progress bars |
| `module_detail.html` | Capítulos do módulo com status icons e botões |
| `chapter_read.html` | Leitura com navegação prev/next e sidebar |

### Documentos

| Arquivo | Descrição |
|---|---|
| `docs/STUDY_PLAN_IMPLEMENTATION.md` | Documento de arquitetura aprovado |
| `docs/STUDY_CONTENT_MAPPING.md` | Mapeamento manual de 14 módulos e 98 capítulos |

### Testes

| Arquivo | Testes |
|---|---|
| `tests/unit/test_plan_service.py` | 10 testes unitários do `PlanService` |
| `tests/integration/test_study_plan_views.py` | 9 testes de integração das views |

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `config/settings/base.py` | `"apps.study_plan"` adicionado a `LOCAL_APPS` |
| `config/urls.py` | `path("plano/", include("apps.study_plan.urls", namespace="study_plan"))` |
| `templates/base.html` | Item "Plano de Estudos" na navbar |

---

## Decisões tomadas

### 1. Mapeamento explícito em vez de parsing de markdown (Ajuste 1)

A arquitetura original propunha parsear headers `##` dos arquivos MASTER. O usuário rejeitou por fragilidade: renomear uma seção quebraria silenciosamente o mapeamento. Solução: `STUDY_PLAN_MAP` no command é uma lista de dataclasses Python com todos os dados explícitos. O `STUDY_CONTENT_MAPPING.md` serve como fonte de verdade legível para humanos; o Python é a fonte de verdade para o sistema.

### 2. `tags = JSONField` no `StudyChapter` (Ajuste 2)

Incluído desde a Fase 1 para a Fase 3 (MiniQuiz). A prioridade de matching será: (1) por tag exata, (2) por disciplina, (3) fallback para qualquer questão. Usar `JSONField` em vez de `ManyToMany` evita uma tabela extra para strings livres.

### 3. `completed_at` preparado para revisão espaçada (Ajuste 3)

O campo `LessonProgress.completed_at` foi incluído pensando em `ScheduledReview` (D+1/D+7/D+21) que será implementado em fase futura. Não há model de revisão agendada na Fase 1.

### 4. `OneToOneField` para `StudyModule.subject`

Cada `Subject` mapeia para no máximo um `StudyModule`. `OneToOneField` reforça isso no banco. Módulo 10 (Revisão Final) tem `subject=None` — o campo é nullable por design.

### 5. Conteúdo dos capítulos vazio na Fase 1

O campo `content` existe nos modelos mas está vazio. O template `chapter_read.html` trata isso com um alerta informativo apontando para o arquivo MASTER. Preencher 98 capítulos é trabalho de curadoria — possível via admin ou um future command `extract_chapter_content`.

### 6. `ChapterReadView` chama `mark_chapter_started` automaticamente

Abrir um capítulo já indica intenção de estudo. Não faz sentido exigir clique explícito para iniciar. A transição `not_started → in_progress` é implícita; a `in_progress → completed` é explícita (botão POST separado).

---

## Problemas encontrados e soluções

### Problema: `ModuleNotFoundError: No module named 'django'`

**Causa:** Execução de `python manage.py makemigrations` sem ativar o virtualenv.  
**Solução:** Todos os comandos Django foram prefixados com `source .venv/bin/activate &&`.

### Problema: Módulo 10 sem `subject_slug`

**Causa:** Revisão Final não corresponde a nenhuma disciplina do banco de questões.  
**Solução:** `subject_slug=None` no `STUDY_PLAN_MAP`. O command imprime warning e continua. O campo `StudyModule.subject` é nullable por design.

### Problema: Idempotência do import

**Verificação:** Segunda execução do command produziu 0 criados, 14+98 atualizados.  
**Mecanismo:** `update_or_create` por `slug` para módulos, por `(module, order)` para capítulos.

---

## Resultado da suíte de testes

```
141 passed, 0 failed, 0 errors
```

Execução: `source .venv/bin/activate && python -m pytest --tb=short -q`

---

## Próximos passos (aguardando aprovação)

### Fase 2 — Aprendizagem Ativa

- Model `ActiveLearningNote` (notas vinculadas a capítulos)
- Model `GuidedReflection` (perguntas de reflexão por módulo)
- Views e templates para criar/listar notas
- Integração na sidebar do `chapter_read.html`

### Fase 3 — Mini Quiz e Caderno de Erros

- `MiniQuizService`: usa `tags` do `StudyChapter` para buscar questões pertinentes
- Integração com `apps.questions.models.Question` (já existente)
- `ErrorNotebook`: registra questões erradas vinculadas ao módulo
- View de mini quiz ao concluir capítulo

### Fase 4 — Calendário e Reta Final

- Calendário de atividade mensal (`get_calendar_activity` já implementado em `PlanService`)
- Módulo 10 (Revisão Final) com lógica específica de reta final
- Dashboard aprimorado com visualização temporal
