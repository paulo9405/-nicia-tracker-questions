# Relatório de Implementação — Fase 4: Progresso, Calendário e Streak

**Data:** 2026-06-30  
**Status:** ✅ Concluída — 216 testes passando (0 falhas)  
**Versão anterior:** 186 testes  
**Novos testes:** +30 (20 unitários + 10 integração)

---

## Arquivos criados

| Arquivo | Linhas | Descrição |
|---|---|---|
| `templates/study_plan/progress.html` | ~170 | Página de progresso: streak cards, calendário mensal, métricas de capítulos, atividades e erros |
| `tests/unit/test_phase4_plan_service.py` | ~165 | 20 testes unitários de `PlanService` |
| `tests/integration/test_phase4_views.py` | ~100 | 10 testes de integração da `ProgressView` |
| `docs/PHASE_4_IMPLEMENTATION_PLAN.md` | ~200 | Plano pré-código |
| `docs/PHASE_4_IMPLEMENTATION.md` | — | Este documento |
| `docs/PHASE_4_MANUAL_TESTING.md` | — | Roteiro de testes manuais |

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `apps/study_plan/services/plan_service.py` | +`ProgressStats` dataclass; +5 métodos novos; atualizado `get_plan_streak` |
| `apps/study_plan/views.py` | +`ProgressView`; +`_MONTH_NAMES_PT` |
| `apps/study_plan/urls.py` | +rota `progresso/` → name `progress` |
| `templates/study_plan/dashboard.html` | Card de streak clicável; botão "Meu progresso" no header |
| `templates/base.html` | Link "Progresso" na navbar |

---

## Decisões tomadas

### 1. Sem novos models

Todos os dados necessários já existiam nas Fases 1–3. A Fase 4 é uma **camada de leitura pura** — agrega dados existentes sem criar tabelas novas e sem migrations.

### 2. `get_all_activity_dates` — union de 4 fontes

Decidido que "dia de estudo" no contexto do Plano de Estudos significa qualquer das 4 ações:
- concluir capítulo
- criar nota de aprendizagem
- responder reflexão guiada
- concluir mini quiz

A union é feita em Python (4 queries com `values_list` + `set.update`) em vez de SQL UNION, pois o volume é pequeno e a legibilidade é maior.

### 3. `get_plan_streak` atualizado

O streak existente usava apenas `LessonProgress.completed_at`. Atualizado para usar `get_all_activity_dates`, tornando o streak mais fiel à realidade do estudo. Os testes existentes continuam passando pois completar um capítulo ainda é uma atividade válida.

### 4. Calendário com `calendar.Calendar(firstweekday=0)`

Semana começa na segunda-feira (padrão brasileiro). `calendar.monthdayscalendar` retorna `0` para os dias de padding (datas fora do mês), tratados no template como células transparentes.

### 5. Navegação por mês via GET params

`?year=YYYY&month=MM` — sem estado em sessão, sem cookie, sem POST. URL compartilhável e bookmarkável. Validação defensiva: valor inválido cai para o mês atual sem erro 500.

### 6. `ProgressStats` como dataclass separado

Optou-se por um novo dataclass em vez de expandir `PlanSummary` para:
- evitar quebrar a API do `PlanSummary` (usada no dashboard e em vários testes existentes)
- separar as responsabilidades: `PlanSummary` é para o dashboard (leve); `ProgressStats` é para a página de progresso (completa)

### 7. Import lazy de `Quiz` no service

`from apps.exams.models import Quiz` é feito dentro dos métodos que o precisam para evitar potencial import circular na inicialização do Django. Na prática os apps são carregados em ordem correta, mas o import lazy é mais seguro e explícito.

---

## Problemas encontrados

### 1. Filtro `split` não existe no Django

O template inicial usava `"Seg,Ter,..."|split:","` para iterar os nomes dos dias da semana. O Django não tem este filtro. Substituído por 7 elementos `<div>` hardcoded — mais simples e sem necessidade de filtro customizado.

---

## Resultado da suíte de testes

```
216 passed, 0 failed, 94 warnings in 4.60s
```

Os 94 warnings são todos `UserWarning: No directory at: .../staticfiles/` — pré-existentes, irrelevantes.

---

## Estatísticas

| Métrica | Valor |
|---|---|
| Testes anteriores | 186 |
| Novos testes unitários | +20 |
| Novos testes integração | +10 |
| **Total** | **216 passando, 0 falhas** |
| Models novos | 0 |
| Migrations novas | 0 |
| Dataclasses novas | 1 (`ProgressStats`) |
| Métodos novos no service | 5 |
| Métodos atualizados | 1 (`get_plan_streak`) |
| Views novas | 1 (`ProgressView`) |
| Templates novos | 1 (`progress.html`) |
| URLs novas | 1 (`/plano/progresso/`) |

---

## Métricas exibidas na ProgressView

| Seção | O que mostra |
|---|---|
| Cards de streak | Streak atual 🔥, maior streak ever, total de dias estudados |
| Calendário | Grade mensal: verde = estudou, cinza = não estudou, borda azul = hoje |
| Progresso | Barra de % geral, capítulos concluídos/total, módulos 100%, em andamento, tempo estimado |
| Aprendizagem | Notas criadas, reflexões feitas |
| Prática | Mini quizzes feitos, erros pendentes (com link para o caderno se pendentes > 0) |
| Estado vazio | Alerta informativo quando `total_study_days == 0` |

---

## Funcionalidades implementadas

1. **ProgressView** — `/plano/progresso/` com todas as métricas acima
2. **Calendário mensal** — navegação entre meses por `?year=&month=`
3. **Streak aprimorado** — streak atual, maior streak ever, total de dias estudados
4. **Atividade unificada** — 4 fontes (capítulos, notas, reflexões, mini quizzes)
5. **Dashboard aprimorado** — card de streak clicável, botão "Meu progresso"
6. **Navbar atualizada** — link "Progresso" entre "Plano de Estudos" e "Caderno de Erros"
7. **Estado vazio** — mensagem e CTA quando não há atividade registrada
8. **UX polish** — cores por faixa de progresso, link para caderno de erros quando pendentes

---

## Limitações

- **Calendário não mostra quantidade** de atividades por dia (só ativo/inativo). Suficiente para o objetivo de "visualizar dias estudados".
- **Tempo estimado** é soma dos `estimated_minutes` dos capítulos concluídos, não tempo real — pois não há controle de tempo real implementado.
- **Mini quizzes contados** como atividade válida se `status=FINISHED`, não `IN_PROGRESS`. Quiz iniciado mas não finalizado não conta.

---

## Próximos passos sugeridos (Fase 5 do Plano)

- **Revisão espaçada automática:** calcular `ErrorNotebookEntry.next_review_at` e sugerir revisões na data certa
- **Metas de estudo:** definir meta diária de capítulos e mostrar progresso vs meta na ProgressView
- **Exportação de progresso:** PDF ou CSV com histórico de estudo
- **Modo de revisão final:** seleção automática de capítulos com menor % de atividade para reta final
