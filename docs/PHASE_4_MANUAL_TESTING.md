# Nícia Track — Roteiro de Testes Manuais — Fase 4

> **Objetivo:** validar a ProgressView, o calendário de atividade, o streak aprimorado, o dashboard aprimorado e a responsividade das novas telas.
>
> **Como usar:** execute cada bloco em ordem, anote ✅ (passou), ❌ (falhou) ou ⚠️ (comportamento estranho, mas não quebrado). Anote a URL e o que viu quando falhar.

---

## Pré-requisitos

1. Servidor rodando: `python manage.py runserver`
2. Banco populado: `python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md`
3. Abrir o navegador em `http://127.0.0.1:8000`
4. Estar logado com um usuário que tem ao menos alguns capítulos concluídos, notas e reflexões criadas.
   - Se o banco estiver limpo: execute os testes do Plano de Estudos (concluir 1–3 capítulos) antes de testar esta fase.

---

## BLOCO 1 — Navbar e acesso

### 1.1 Link "Progresso" na navbar

| # | Ação | Rota | Comportamento esperado |
|---|---|---|---|
| 1.1.1 | Olhe a navbar logado | qualquer rota | Link "📊 Progresso" aparece entre "Plano de Estudos" e "Caderno de Erros" | ✅ (passou)
| 1.1.2 | Clique em "Progresso" | `—` | Redireciona para `/plano/progresso/` | ✅ (passou)
| 1.1.3 | Acesse sem estar logado | `/plano/progresso/` | Redireciona para `/conta/login/?next=/plano/progresso/` |✅ (passou)

---

## BLOCO 2 — ProgressView

**Rota:** `http://127.0.0.1:8000/plano/progresso/`

### 2.1 Acesso e estrutura geral

| # | Ação | Comportamento esperado |
|---|---|---|
| 2.1.1 | Acesse `/plano/progresso/` logado | Página carrega com título "Meu Progresso" e botão "Voltar ao Plano" | ✅ (passou)
| 2.1.2 | Clique em "Voltar ao Plano" | Redireciona para `/plano/` |✅ (passou)
| 2.1.3 | Verifique a estrutura geral | 3 cards de streak + calendário + seção de progresso + seção de atividades |✅ (passou)

---

### 2.2 Cards de streak

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 2.2.1 | Card "Streak atual" | Mostra número + 🔥. Se 0, exibe "Estude hoje para começar!" | ✅ (passou)
| 2.2.2 | Card "Maior streak" | Número igual ou maior que o streak atual |✅ (passou)
| 2.2.3 | Card "Dias estudados" | Total de dias distintos com atividade. >= streak atual | ✅ (passou)
| 2.2.4 | Cor do streak atual | Amarelo (`text-warning`) se >= 3 dias, cinza se < 3 |✅ (passou)
| 2.2.5 | Com streak = 0 | Cards mostram 0 sem erros. Mensagem motivacional no card atual | ✅ (passou)
---

### 2.3 Calendário

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 2.3.1 | Calendário exibe mês atual | Título "Mês Ano" correto (ex.: "Junho 2026") | ✅ (passou)
| 2.3.2 | Grade do calendário | 7 colunas (Seg, Ter, Qua, Qui, Sex, Sáb, Dom), N linhas de semanas |✅ (passou)
| 2.3.3 | Dia de hoje | Célula de hoje tem borda azul (destaque) |✅ (passou)
| 2.3.4 | Dia com atividade | Quadrado verde |✅ (passou)
| 2.3.5 | Dia sem atividade (do mês atual) | Quadrado cinza claro |✅ (passou)
| 2.3.6 | Dias de padding (fora do mês) | Célula transparente/vazia |✅ (passou)
| 2.3.7 | Legenda | "🟩 Estudou / ⬜ Não estudou" aparece abaixo do calendário |✅ (passou)
| 2.3.8 | Botão ◄ (mês anterior) | Navega para o mês anterior sem erros |✅ (passou)
| 2.3.9 | Botão ► (mês seguinte) | Navega para o mês seguinte sem erros |✅ (passou)
| 2.3.10 | Mês sem atividade | Todos os quadrados cinzas, nenhum verde |✅ (passou)
| 2.3.11 | Navegação para Janeiro | Prev do mês 1 vai para Dezembro do ano anterior |✅ (passou)
| 2.3.12 | Navegação para Dezembro | Next do mês 12 vai para Janeiro do ano seguinte |✅ (passou)

---

### 2.4 Seção de progresso de capítulos

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 2.4.1 | Barra de progresso | Exibe percentual correto. Cor: verde ≥80%, azul ≥50%, amarelo ≥20%, cinza <20% |✅ (passou)
| 2.4.2 | Texto "X/Y (ZZ%)" | Números coerentes com atividade do usuário |✅ (passou)
| 2.4.3 | Card "Módulos concluídos" | 0 se nenhum módulo foi 100% concluído; N se algum foi |✅ (passou)
| 2.4.4 | Card "Em andamento" | Número de capítulos com status IN_PROGRESS |✅ (passou)
| 2.4.5 | Card "Tempo estimado" | Soma dos `estimated_minutes` dos capítulos concluídos, em min. Se 0 capítulos: "—" | ✅ (passou)
| 2.4.6 | Card "Total de módulos" | Número total de módulos ativos no plano |✅ (passou)

---

### 2.5 Seção de atividades de aprendizagem

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 2.5.1 | "Notas criadas" | Número correto de notas de aprendizagem ativa criadas pelo usuário | ✅ (passou)
| 2.5.2 | "Reflexões feitas" | Número correto de reflexões guiadas criadas | ✅ (passou)
| 2.5.3 | Estado vazio (sem notas) | "Conclua um capítulo e registre sua primeira nota!" aparece | ✅ (passou)
| 2.5.4 | "Mini quizzes feitos" | Número de Quiz[MINI, FINISHED] do usuário |✅ (passou)
| 2.5.5 | "Erros pendentes" com 0 | Número em cinza, sem botão de revisão |✅ (passou)
| 2.5.6 | "Erros pendentes" > 0 | Número em vermelho + botão "Revisar erros" |✅ (passou)
| 2.5.7 | Botão "Revisar erros" | Redireciona para `/plano/caderno-de-erros/` | ✅ (passou)
| 2.5.8 | Todos erros revisados | Mensagem "Todos os N erros revisados!" em verde |✅ (passou)

---

### 2.6 Estado vazio (sem nenhuma atividade)

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 2.6.1 | Usuário novo sem atividade | Alerta azul "Ainda sem atividade registrada." aparece | ✅ (passou)
| 2.6.2 | Botão no alerta | "Ir para o Plano de Estudos" redireciona para `/plano/` |✅ (passou)
| 2.6.3 | Métricas com 0 | Todos os números são 0 ou "—" sem erros |✅ (passou)

---

## BLOCO 3 — Streak aprimorado

### 3.1 Validar as fontes de atividade

O streak agora conta qualquer atividade: capítulo concluído, nota criada, reflexão respondida, ou mini quiz concluído.

| # | Ação | Comportamento esperado |
|---|---|---|
| 3.1.1 | Conclua um capítulo (sem nota, sem reflexão) | Streak aumenta 1 (hoje conta) | ✅ (passou)
| 3.1.2 | Crie apenas uma nota (sem completar capítulo) | Streak = 1 hoje (nota conta como atividade) | ✅ (passou)
| 3.1.3 | Responda apenas uma reflexão | Streak = 1 hoje | ✅ (passou)
| 3.1.4 | Faça um mini quiz até o fim | Streak = 1 hoje | ✅ (passou)

---

### 3.2 Cálculo do streak

| # | Cenário | Comportamento esperado |
|---|---|---|
| 3.2.1 | Sem nenhuma atividade | Streak atual = 0, maior streak = 0 |✅ (passou)
| 3.2.2 | Atividade só hoje | Streak atual = 1 |✅ (passou)
| 3.2.3 | Atividade ontem e hoje | Streak atual = 2 |✅ (passou)
| 3.2.4 | Atividade há 3 dias, gap de 2, hoje | Streak atual = 1 (quebrou) |✅ (passou)
| 3.2.5 | Maior streak > streak atual | "Maior streak" mostra o valor histórico correto |✅ (passou)

---

## BLOCO 4 — Dashboard aprimorado

**Rota:** `http://127.0.0.1:8000/plano/`

### 4.1 Card de streak clicável

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 4.1.1 | Card de streak | É clicável e leva para `/plano/progresso/` |✅ (passou)
| 4.1.2 | Texto "Ver progresso →" | Aparece em azul dentro do card de streak |✅ (passou)
| 4.1.3 | Hover no card | Efeito visual de elevação (transição CSS) |✅ (passou)

---

### 4.2 Botão "Meu progresso" no header

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 4.2.1 | Header do plano | Botão verde "Meu progresso" aparece ao lado de "Ver módulos" |  ✅ (passou)
| 4.2.2 | Clique em "Meu progresso" | Leva para `/plano/progresso/` | ✅ (passou)
| 4.2.3 | Botão "Ver módulos" | Ainda funciona e leva para `/plano/modulos/` | ✅ (passou)

---

## BLOCO 5 — Responsividade

### 5.1 Mobile (375px)

| # | Tela | O que verificar |
|---|---|---|
| 5.1.1 | `/plano/progresso/` | Cards de streak: 2 em linha na primeira fileira, 1 na segunda (col-6 col-md-4) | ✅ (passou)
| 5.1.2 | Calendário mobile | Grade cabe na tela sem overflow horizontal. Números legíveis |✅ (passou)
| 5.1.3 | Cabeçalho do calendário | "Seg Ter Qua..." legíveis em 7 colunas |✅ (passou)
| 5.1.4 | Seção de métricas | Cards de 2 em 2 (col-6 col-md-3) |✅ (passou)
| 5.1.5 | Botões de navegação ◄/► | Acessíveis e tocáveis |✅ (passou)

---

### 5.2 Tablet (768px)

| # | Tela | O que verificar |
|---|---|---|
| 5.2.1 | Cards de streak | 3 em linha (col-md-4) |✅ (passou)
| 5.2.2 | Calendário | Grade confortável, células com espaçamento adequado |✅ (passou)

---

### 5.3 Desktop (1280px)

| # | Tela | O que verificar |
|---|---|---|
| 5.3.1 | Layout geral | Colunas corretas, sem elementos cortados | ✅ (passou)
| 5.3.2 | Calendário | Células quadradas com tamanho razoável |✅ (passou)

---

## BLOCO 6 — Fluxo de ponta a ponta

Execute este bloco simulando a Nícia usando o sistema pela primeira vez nesta fase.

| # | Passo | Comportamento esperado |
|---|---|---|
| 6.1 | Logue no sistema | Dashboard do Plano de Estudos aparece |✅ (passou)
| 6.2 | Clique em "Meu progresso" no header | Vai para `/plano/progresso/` |✅ (passou)
| 6.3 | Verifique o calendário | Mês atual, dias estudados marcados em verde |✅ (passou)
| 6.4 | Navegue para o mês anterior com ◄ | Calendário muda, URL atualiza `?year=&month=` |✅ (passou)
| 6.5 | Volte ao mês atual com ► | Calendário volta ao mês correto |✅ (passou)
| 6.6 | Observe o streak | Streak atual correto; maior streak >= streak atual |✅ (passou)
| 6.7 | Volte ao dashboard | Botão "Voltar ao Plano" funciona |✅ (passou)
| 6.8 | Clique no card de streak no dashboard | Vai para `/plano/progresso/` |✅ (passou)
| 6.9 | Conclua um novo capítulo via Plano de Estudos | Volte ao progresso; capítulos concluídos aumentou |✅ (passou)
| 6.10 | Crie uma nota no capítulo recém-concluído | Total de notas aumentou na ProgressView |✅ (passou)
| 6.11 | Faça um mini quiz via Plano de Estudos | Total de mini quizzes aumentou na ProgressView |✅ (passou)

---

## Checklist final

| Funcionalidade | Status |
|---|---|
| Link "Progresso" na navbar | ☐ |
| ProgressView carrega sem erro | ☐ |
| Cards de streak corretos | ☐ |
| Calendário renderiza corretamente | ☐ |
| Dias estudados marcados em verde | ☐ |
| Navegação entre meses funciona | ☐ |
| Borda azul no dia de hoje | ☐ |
| Seção de progresso de capítulos | ☐ |
| Seção de atividades (notas/reflexões/quizzes) | ☐ |
| Estado vazio com CTA | ☐ |
| Link "Revisar erros" quando pendentes > 0 | ☐ |
| Card de streak clicável no dashboard | ☐ |
| Botão "Meu progresso" no dashboard | ☐ |
| Responsividade mobile (375px) | ☐ |
| Responsividade tablet (768px) | ☐ |
| Responsividade desktop (1280px) | ☐ |
| Fluxo de ponta a ponta completo | ☐ |

---

## Registro de bugs

| # | Bloco | Passo | URL | O que aconteceu | O que deveria acontecer | Prioridade |
|---|---|---|---|---|---|---|
| | | | | | | |

**Prioridade:** 🔴 Quebra o sistema / 🟡 Comportamento errado mas não impede uso / 🟢 Visual/UX menor
