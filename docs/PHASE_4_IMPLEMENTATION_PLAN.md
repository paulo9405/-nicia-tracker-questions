# Plano de Implementação — Fase 4: Progresso, Calendário e Streak

**Data:** 2026-06-30  
**Objetivo:** completar a experiência do Plano de Estudos com visualização de progresso, acompanhamento de consistência e polimento de UX.

---

## 1. Models utilizados (sem novos models)

Todos os dados necessários já existem nos models das Fases 1–3:

| Model | App | O que fornece para a Fase 4 |
|---|---|---|
| `LessonProgress` | study_plan | capítulos concluídos, datas (`completed_at`), minutos estimados |
| `ActiveLearningNote` | study_plan | notas criadas (`created_at`) |
| `GuidedReflection` | study_plan | reflexões criadas (`created_at`) |
| `ErrorNotebookEntry` | study_plan | erros pendentes / revisados |
| `StudyModule` | study_plan | total de módulos |
| `StudyChapter` | study_plan | total de capítulos |
| `Quiz` (type=MINI) | exams | mini quizzes concluídos (`finished_at`) |

**Decisão:** nenhum model novo é necessário. O Phase 4 é uma camada de **leitura e agregação** sobre os dados existentes.

---

## 2. Services utilizados

### `PlanService` — extensões

Todos os novos métodos serão adicionados em `apps/study_plan/services/plan_service.py`.

#### 2a. Novo dataclass `ProgressStats`

```python
@dataclass
class ProgressStats:
    # Capítulos e módulos
    total_modules: int
    completed_modules: int
    total_chapters: int
    completed_chapters: int
    in_progress_chapters: int
    overall_percentage: float

    # Aprendizagem ativa
    notes_created: int
    reflections_created: int

    # Quizzes
    mini_quizzes_done: int

    # Caderno de erros
    errors_pending: int
    errors_reviewed: int

    # Streak e consistência
    current_streak: int
    max_streak: int
    total_study_days: int

    # Tempo estimado (sum de estimated_minutes dos capítulos concluídos)
    total_minutes_estimated: int
```

#### 2b. `get_all_activity_dates(user) -> set[date]`

União de todas as datas com atividade relevante:
- `LessonProgress.completed_at__date` (capítulos concluídos)
- `ActiveLearningNote.created_at__date` (notas criadas)
- `GuidedReflection.created_at__date` (reflexões criadas)
- `Quiz(type=MINI, status=FINISHED).finished_at__date` (mini quizzes concluídos)

**Por que este conjunto?** O escopo do Plano de Estudos define "estudo válido" como qualquer interação com o conteúdo — não apenas conclusão de capítulo. Nota + reflexão + mini quiz são partes igualmente válidas do fluxo de aprendizagem.

#### 2c. Atualização de `get_plan_streak(user) -> int`

Atualizar para usar `get_all_activity_dates` em vez de apenas capítulos concluídos. Os testes existentes continuam passando pois completar um capítulo ainda conta como atividade.

#### 2d. `get_max_streak(user) -> int`

Ordena as datas de atividade e percorre encontrando a maior sequência consecutiva.

```
dates = sorted(get_all_activity_dates(user))
max_s = 1, current_s = 1
for i in 1..N:
    if dates[i] - dates[i-1] == 1 dia: current_s++, max_s = max(max_s, current_s)
    else: current_s = 1
```

#### 2e. `get_total_study_days(user) -> int`

`len(get_all_activity_dates(user))`.

#### 2f. `get_calendar_weeks(user, year, month) -> list`

Retorna grade do calendário para o template. Usa `calendar.Calendar(firstweekday=0)` (segunda-feira no início).

Cada semana é uma lista de 7 tuplas `(day: int, active: bool)`:
- `day=0` → padding (dia fora do mês)
- `active=True` → houve atividade nesse dia

#### 2g. `get_progress_stats(user) -> ProgressStats`

Agrega todas as métricas em uma única chamada otimizada.

---

## 3. Novas views

### `ProgressView`

**URL:** `GET /plano/progresso/`  
**Template:** `study_plan/progress.html`  
**Arquivo:** `apps/study_plan/views.py`

Contexto passado:
- `stats` — `ProgressStats`
- `calendar_weeks` — grade do calendário
- `calendar_year`, `calendar_month` — mês exibido
- `calendar_month_name` — nome do mês em português
- `prev_year`, `prev_month` — navegação ◄
- `next_year`, `next_month` — navegação ►

Suporte a parâmetros GET `?year=YYYY&month=MM` para navegação entre meses.

---

## 4. Templates novos e alterados

### 4a. `study_plan/progress.html` (NOVO)

Seções:
1. **Header** — título + botão voltar ao plano
2. **Cards de streak** — streak atual / maior streak / total de dias estudados
3. **Métricas gerais** — progresso de capítulos, módulos, notas, reflexões, quizzes, erros
4. **Calendário mensal** — grade visual com quadrados coloridos

Calendário:
- 🟩 verde = estudou / ⬜ cinza claro = não estudou / 🔲 transparente = fora do mês
- Cabeçalho com dia da semana
- Navegação por mês com links `?year=&month=`
- Destaque para "hoje" com borda diferente

### 4b. `study_plan/dashboard.html` (ALTERADO)

Adições:
- Link "Ver progresso →" junto ao card de streak
- Contagem de notas + reflexões criadas (linha extra abaixo dos 4 cards principais)
- Contagem de erros pendentes no notebook

Restrição: não substituir nenhum conteúdo existente, apenas acrescentar.

### 4c. `base.html` (ALTERADO)

Adicionar link "Progresso" na navbar entre "Plano de Estudos" e "Caderno de Erros".

---

## 5. Cálculo do streak

**Definição:** número de dias consecutivos com pelo menos uma atividade de estudo até hoje (ou ontem, se não estudou hoje ainda).

**Fontes de atividade** (unionadas):
1. Capítulos concluídos (`LessonProgress.completed_at`)
2. Notas de aprendizagem criadas (`ActiveLearningNote.created_at`)
3. Reflexões respondidas (`GuidedReflection.created_at`)
4. Mini quizzes concluídos (`Quiz[MINI].finished_at`)

**Algoritmo:**
```
today = date.today()
streak = 0
current = today
while current in all_activity_dates:
    streak++
    current = current - 1 dia

# Se não estudou hoje, verifica desde ontem
if streak == 0:
    current = today - 1 dia
    while current in all_activity_dates:
        streak++
        current = current - 1 dia
```

**Maior streak:** percorre todas as datas em ordem crescente, encontra a maior sequência consecutiva.

---

## 6. Cálculo do calendário

```python
import calendar

c = calendar.Calendar(firstweekday=0)  # segunda-feira = início da semana
weeks = c.monthdayscalendar(year, month)  # lista de listas de 7 ints (0 = padding)

all_dates = get_all_activity_dates(user)
month_active = {d for d in all_dates if d.year == year and d.month == month}

result = []
for week in weeks:
    week_data = []
    for day in week:
        if day == 0:
            week_data.append((0, False))
        else:
            d = date(year, month, day)
            week_data.append((day, d in month_active))
    result.append(week_data)
```

O template itera sobre `calendar_weeks` e renderiza cada célula.

---

## 7. Métricas exibidas na ProgressView

| Seção | Métrica | Fonte |
|---|---|---|
| Streak | Streak atual | `get_all_activity_dates` + algoritmo |
| Streak | Maior streak | `get_max_streak` |
| Streak | Total de dias estudados | `len(get_all_activity_dates)` |
| Progresso | % geral | `completed_chapters / total_chapters * 100` |
| Progresso | Capítulos concluídos / total | `LessonProgress.COMPLETED` |
| Progresso | Módulos 100% concluídos | módulos onde todos capítulos estão COMPLETED |
| Atividades | Notas criadas | `ActiveLearningNote.count(user)` |
| Atividades | Reflexões criadas | `GuidedReflection.count(user)` |
| Atividades | Mini quizzes feitos | `Quiz(type=MINI, status=FINISHED).count(user)` |
| Erros | Pendentes de revisão | `ErrorNotebookEntry(is_reviewed=False).count(user)` |
| Erros | Já revisados | `ErrorNotebookEntry(is_reviewed=True).count(user)` |
| Tempo | Minutos estimados (capítulos concluídos) | `SUM(chapter.estimated_minutes)` para capítulos com LessonProgress.COMPLETED |

---

## 8. Integração com as fases anteriores

| Fase | Como a Fase 4 consome |
|---|---|
| Fase 1 (Plano) | `LessonProgress`, `StudyModule`, `StudyChapter` para métricas e calendário |
| Fase 2 (Notas) | `ActiveLearningNote`, `GuidedReflection` para métricas e datas de atividade |
| Fase 3 (Quiz+Erros) | `ErrorNotebookEntry` para erros pendentes; `Quiz[MINI]` para mini quizzes feitos |

---

## 9. Impacto na arquitetura atual

- **Sem novos models** → sem migrations
- **Sem novos forms** → sem formulários
- **1 nova view** → `ProgressView` (read-only)
- **1 novo template** → `progress.html`
- **Extensão do service** → `PlanService` recebe ~5 métodos novos e 1 dataclass
- **Extensão de 2 templates existentes** → `dashboard.html` e `base.html`

Performance: todos os cálculos são queries simples com filtros indexados. O calendário de um mês requer no máximo 4 queries. Sem necessidade de cache para o volume atual.

---

## 10. Testes

### Unitários (test_phase4_plan_service.py) — ~11 testes
- `get_all_activity_dates` com 0, 1 e múltiplas fontes
- `get_max_streak` com 0, 1, vários dias consecutivos, gap
- `get_total_study_days`
- `get_calendar_weeks` — estrutura e atividade correta
- `get_progress_stats` — campos preenchidos corretamente

### Integração (test_phase4_views.py) — ~5 testes
- `ProgressView` requer login
- `ProgressView` renderiza com usuário logado
- `ProgressView` sem atividade → valores zerados
- `ProgressView` aceita `?year=&month=` sem erro
- `ProgressView` tem keys obrigatórias no contexto

**Total esperado:** 186 + 16 = ~202 testes passando.

---

## 11. Ordem de implementação

1. Estender `plan_service.py` (dataclass + métodos)
2. Adicionar `ProgressView` em `views.py`
3. Adicionar rota em `urls.py`
4. Criar `progress.html`
5. Atualizar `dashboard.html`
6. Atualizar `base.html`
7. Escrever e rodar testes
8. Criar `PHASE_4_IMPLEMENTATION.md`
9. Criar `PHASE_4_MANUAL_TESTING.md`
10. Atualizar `PROJECT_EXPLAINED.md`
