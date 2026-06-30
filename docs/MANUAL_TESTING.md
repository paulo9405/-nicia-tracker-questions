# Nícia Track — Roteiro de Testes Manuais

> **Objetivo:** percorrer cada funcionalidade do sistema, documentar o comportamento esperado e anotar qualquer desvio encontrado.
>
> **Como usar:** execute cada bloco em ordem, anote ✅ (passou), ❌ (falhou) ou ⚠️ (comportamento estranho, mas não quebrado) em cada item. Anote a URL e o que viu quando falhar.

---

## Pré-requisitos

1. Servidor rodando: `python manage.py runserver` ✅ (passou)
2. Banco populado: `python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md` ✅ (passou)
3. Abrir o navegador em `http://127.0.0.1:8000` ✅ (passou)
4. Ter duas abas abertas: uma para o usuário principal, outra para testar isolamento de sessão. ✅ (passou)

---

## BLOCO 1 — Autenticação

### 1.1 Acesso sem login (proteção de rotas)

| # | Ação | Rota | Comportamento esperado |
|---|---|---|---|
| 1.1.1 | Acesse sem estar logado | `http://127.0.0.1:8000/` | Redireciona para `/conta/login/?next=/` | ✅ (passou)
| 1.1.2 | Acesse sem estar logado | `http://127.0.0.1:8000/questoes/` | Redireciona para `/conta/login/?next=/questoes/` | ❌ (falhou) redireciona para (Page not found (404))
| 1.1.3 | Acesse sem estar logado | `http://127.0.0.1:8000/estatisticas/` | Redireciona para `/conta/login/?next=/estatisticas/` | ✅ (passou)
| 1.1.4 | Acesse sem estar logado | `http://127.0.0.1:8000/conta/perfil/` | Redireciona para `/conta/login/?next=/conta/perfil/` | ✅ (passou)

---

### 1.2 Cadastro — `/conta/cadastro/`

| # | Ação | Comportamento esperado |
|---|---|---|
| 1.2.1 | Acesse a rota de cadastro | Exibe formulário com campos: nome, sobrenome, e-mail, senha, confirmar senha | ✅ (passou)

| 1.2.2 | Submeta o formulário **vazio** | Exibe mensagens de erro em cada campo obrigatório. Não cria usuário. | ✅ (passou) — corrigido: nome e sobrenome agora são obrigatórios |

| 1.2.3 | E-mail inválido (ex.: `nao-e-email`) | Campo e-mail exibe erro de validação. | ✅ (passou)

| 1.2.4 | Senhas diferentes nos dois campos | Exibe erro "As senhas não coincidem" (ou equivalente). Não cria usuário. | ✅ (passou)

| 1.2.5 | Preencha tudo corretamente e submeta | Cria o usuário, loga automaticamente e redireciona para o perfil (ou dashboard). Exibe mensagem de sucesso. | ✅ (passou)

| 1.2.6 | Tente cadastrar o mesmo e-mail de novo | Exibe erro "E-mail já cadastrado" (ou equivalente). Não cria usuário duplicado. | ✅ (passou)
| 1.2.7 | Acesse `/conta/cadastro/` **já logado** | Redireciona para o dashboard (não exibe o formulário novamente). | ✅ (passou) — corrigido |

---

### 1.3 Login — `/conta/login/`

| # | Ação | Comportamento esperado |
|---|---|---|
| 1.3.1 | Acesse a rota de login | Exibe formulário com campos e-mail e senha. | ✅ (passou)

| 1.3.2 | Submeta **vazio** | Exibe erros de validação. | ✅ (passou)

| 1.3.3 | E-mail correto, senha errada | Exibe mensagem de erro de autenticação. Não loga. | ✅ (passou)

| 1.3.4 | E-mail inexistente | Exibe mensagem de erro de autenticação. | ✅ (passou)

| 1.3.5 | Credenciais corretas | Loga e redireciona para o dashboard (`/`). | ✅ (passou) — corrigido |

| 1.3.6 | Acesse `/conta/login/` **já logado** | Redireciona para o dashboard sem exibir o formulário. | ✅ (passou) — corrigido |

---

### 1.4 Logout — `/conta/logout/`

| # | Ação | Comportamento esperado |
|---|---|---|
| 1.4.1 | Acesse `/conta/logout/` logado | Exibe **página de confirmação** de logout (não desloga imediatamente). | ✅ (passou) — corrigido: botão "Sair" na navbar agora abre página de confirmação |

| 1.4.2 | Clique no botão "Confirmar logout" (POST) | Desloga e redireciona para o login. | ✅ (passou)
| 1.4.3 | Tente acessar `/conta/logout/` via GET com link externo (simule colando a URL) | Deve exibir a tela de confirmação — nunca deslogar via GET silenciosamente. | ✅ (passou) — sem login redireciona para `/conta/login/?next=/conta/logout/`; com login exibe a página de confirmação |

| 1.4.4 | Acesse qualquer rota protegida após logout | Redireciona para o login. | ✅ (passou)

---

### 1.5 Perfil — `/conta/perfil/`

| # | Ação | Comportamento esperado |
|---|---|---|
| 1.5.1 | Acesse logado | Exibe formulário com nome, sobrenome e demais campos de perfil (meta diária, concurso-alvo, etc.). | ✅ (passou)

| 1.5.2 | Altere o nome e salve | Salva e exibe mensagem de sucesso. O nome atualizado aparece na navbar. | ✅ (passou)
| 1.5.3 | Altere a meta diária (ex.: 20 questões) | Salva corretamente. O valor novo aparece no dashboard. | ✅ (passou)
| 1.5.4 | Salve sem alterar nada | Salva sem erro. | ✅ (passou)

---

## BLOCO 2 — Dashboard

**Rota:** `http://127.0.0.1:8000/`

### 2.1 Estado inicial (usuário sem treinos)

| # | Ação | Comportamento esperado |
|---|---|---|
| 2.1.1 | Acesse o dashboard recém-cadastrado | Exibe estado vazio: ícone/saudação e botão "Começar primeiro treino". | ✅ (passou)

| 2.1.2 | Verifique a navbar | Contém links: Dashboard, Questões, Simulado, Estatísticas, Perfil/Sair. Todos funcionando. | ✅ (passou)

| 2.1.3 | Clique em "Começar primeiro treino" | Redireciona para `/questoes/`. | ✅ (passou)

---

### 2.2 Dashboard com dados (após realizar treinos)

> Execute este bloco **após** completar ao menos 2 treinos no Bloco 3.

| # | O que verificar | Comportamento esperado |
|---|---|---|
| 2.2.1 | Card "Respondidas" | Exibe o total correto de questões respondidas. | ✅ (passou)
| 2.2.2 | Card "Acertos" | Total de acertos compatível com os treinos feitos. | ✅ (passou)
| 2.2.3 | Card "Erros" | Total de erros compatível. | ✅ (passou)
| 2.2.4 | Card "Aproveitamento %" | Percentual correto; cor verde ≥70%, amarelo ≥50%, vermelho <50%. | ✅ (passou)
| 2.2.5 | Card "🔥 Streak" | Exibe 1 se estudou hoje. Exibe 0 se ainda não estudou hoje. | ✅ (passou)
| 2.2.6 | Card "Treinos realizados" | Quantidade bate com o número de treinos finalizados. | ✅ (passou)
| 2.2.7 | Card "Meta diária" | Barra de progresso reflete questões respondidas hoje vs meta do perfil. | ✅ (passou)
| 2.2.8 | Seção "Desempenho por disciplina" | Aparece com barras coloridas para cada disciplina treinada. | ✅ (passou)
| 2.2.9 | Seção "Treinos recentes" | Exibe até 5 treinos com link "Ver" para o gabarito. | ✅ (passou)
| 2.2.10 | Clique em "Ver" em um treino recente | Abre o resultado do treino correto. | ✅ (passou)

---

## BLOCO 3 — Banco de Questões (Treino)

**Rota inicial:** `http://127.0.0.1:8000/questoes/`

### 3.1 Filtros

| # | Ação | Comportamento esperado |
|---|---|---|
| 3.1.1 | Acesse `/questoes/` | Exibe formulário com select de disciplinas, select de tópicos e opções de quantidade (10, 20, 50). | ⚠️ tópicos não aparecem — o banco de questões não possui tópicos cadastrados (limitação dos dados, não do código)

| 3.1.2 | Selecione uma disciplina | O select de tópicos filtra e exibe apenas os tópicos daquela disciplina. | ⚠️ código corrigido (data-subject adicionado), mas não há tópicos no banco para exibir — pendente para quando tópicos forem importados

| 3.1.3 | Troque de disciplina | O select de tópicos atualiza para os tópicos da nova disciplina. | ⚠️ mesmo motivo de 3.1.2 — sem dados de tópico no banco

| 3.1.4 | Tente submeter sem selecionar disciplina | Exibe erro ou não prossegue. | ✅ (passou)

| 3.1.5 | Selecione disciplina, nenhum tópico e 10 questões e submeta | Cria o quiz e redireciona para `/questoes/treino/<uuid>/`. | ✅ (passou)

| 3.1.6 | Selecione disciplina + tópico e 10 questões | Cria o quiz com questões apenas daquele tópico. | ✅ (passou)

---

### 3.2 Resolução — `/questoes/treino/<uuid>/`

| # | Ação | Comportamento esperado |
|---|---|---|

| 3.2.1 | Acesse a URL do treino | Exibe todas as questões na página (modo prova em papel). | ✅ (passou)

| 3.2.2 | Verifique numeração | Questões numeradas de 1 a N. | ✅ (passou)

| 3.2.3 | Verifique alternativas | Cada questão tem opções A, B, C, D como radio buttons (selecionar uma desmarca as demais). | ✅ (passou)

| 3.2.4 | Questões de Português com texto-base | O texto-base aparece em destaque antes das questões que dependem dele. | ✅ (passou)

| 3.2.5 | Marque todas as questões e clique em "Finalizar" | Exibe diálogo de confirmação. Ao confirmar, submete e redireciona para resultado. | ✅ (passou)

| 3.2.6 | Clique em "Finalizar" com questões em branco | Exibe diálogo de confirmação (com aviso de questões sem resposta, se implementado). | ✅ (passou) 

| 3.2.7 | **Sem marcar nada**, clique em "Finalizar" e confirme | Submete com todas as questões puladas. Redireciona para resultado. | ✅ (passou)

| 3.2.8 | Acesse a URL do treino já **finalizado** | Redireciona automaticamente para a tela de resultado. | ✅ (passou)

| 3.2.9 | Navegação rápida (links de número no topo ou lateral) | Leva à âncora correta da questão na página. | (esse teste eu nao entendi)

---

### 3.3 Resultado — `/questoes/resultado/<uuid>/`

| # | Ação | Comportamento esperado |
|---|---|---|
| 3.3.1 | Acesse a tela de resultado | Exibe card de resumo: acertos, erros, puladas, percentual, barra de progresso. | ✅ (passou)
| 3.3.2 | Ícone/emoji do resultado | Verde/troféu se ≥70%, amarelo/smile se ≥50%, vermelho/frown se <50%. |✅ (passou)
| 3.3.3 | Lista de questões | Cada questão aparece com cor: verde (acerto), vermelho (erro), cinza (pulada). | ✅ (passou)

| 3.3.4 | Alternativas por questão | ✓ na correta, ✗ na que o usuário marcou errado, ○ nas demais. |✅ (passou)

| 3.3.5 | Explicação/comentário | Aparece abaixo de cada questão. | ✅ (passou)

| 3.3.6 | Questão pulada | Mostra como "pulada" e indica a alternativa correta. | ✅ (passou)

| 3.3.7 | Acesse resultado de quiz **em andamento** | Redireciona automaticamente para a tela de resolução. | ✅ (passou)

| 3.3.8 | Botão "Treinar novamente" ou equivalente | Funciona e leva de volta aos filtros. | ✅ (passou)

---

### 3.4 Isolamento de usuário (segurança)

| # | Ação | Comportamento esperado |
|---|---|---|
| 3.4.1 | Copie a URL de um treino (`/questoes/treino/<uuid>/`) e abra em uma aba não logada (ou com outro usuário) | Redireciona para login (aba não logada) ou retorna 404/403 (outro usuário). |  ✅ (passou) direciona para login

| 3.4.2 | Copie a URL de um resultado e acesse com outro usuário logado | Retorna 404 — o quiz não pertence ao outro usuário. | ✅ (passou), page not found, com o log, acho q pq e debug true

---

## BLOCO 4 — Simulado

**Rota inicial:** `http://127.0.0.1:8000/questoes/simulado/`

### 4.1 Página inicial do simulado

| # | Ação | Comportamento esperado |
|---|---|---|
| 4.1.1 | Acesse `/questoes/simulado/` | Exibe landing page com: distribuição de questões (5+5+5+5+20), duração (3h), botão "Iniciar simulado". | ✅ (passou)

| 4.1.2 | Verifique o alerta de aviso | Deve informar que o cronômetro começa ao iniciar e que fechar e retornar preserva as respostas. | ✅ (passou)

---

### 4.2 Criação e resolução

| # | Ação | Comportamento esperado |
|---|---|---|

| 4.2.1 | Clique em "Iniciar simulado" | Cria o simulado (40 questões) e redireciona para `/questoes/simulado/<uuid>/`. | ✅ (passou)

| 4.2.2 | Verifique cabeçalho sticky | Deve mostrar: título "Simulado", contagem de questões, cronômetro regressivo (3:00:00), botão "Finalizar". |  ✅ (passou)

| 4.2.3 | Verifique o cronômetro | Está contando para baixo em tempo real. | ✅ (passou)

| 4.2.4 | Verifique badges de disciplina | Cada questão tem badge colorido com o nome da disciplina. | ✅ (passou)

| 4.2.5 | Marque algumas respostas e recarregue a página (F5) | As marcações são preservadas (localStorage). O cronômetro continua de onde parou. | ✅ (passou)

| 4.2.6 | Verifique botões de navegação | Ficam sólidos/coloridos ao marcar a questão correspondente. | ✅ (passou)

| 4.2.7 | Verifique distribuição | Deve ter exatamente: 5 Português + 5 Matemática + 5 Informática + 5 Conhec. Gerais + 20 Específicas = 40 total. | ✅ (passou)

| 4.2.8 | Clique em "Finalizar" com questões em branco | Exibe aviso de quantas questões estão sem resposta. Permite confirmar ou cancelar. | ✅ (passou)

| 4.2.9 | Finalize o simulado | Submete, limpa localStorage, redireciona para resultado. | ✅ (passou)

---

### 4.3 Resultado do simulado

| # | Ação | Comportamento esperado |
|---|---|---|
| 4.3.1 | Tela de resultado do simulado | Título mostra "Simulado" (não nome de disciplina). | ✅ (passou)

| 4.3.2 | Seção "Resultado por disciplina" | Aparece com barras por disciplina (Português, Matemática, etc.) antes do gabarito. | ✅ (passou)

| 4.3.3 | Gabarito questão a questão | Igual ao treino: verde/vermelho/cinza, alternativas com ícones. | ✅ (passou)

| 4.3.4 | Botão de ação | Deve ser "Novo simulado" (não "Treinar novamente"). | ✅ (passou)

---

### 4.4 Guard de simulado ativo

| # | Ação | Comportamento esperado |
|---|---|---|
| 4.4.1 | Com simulado em andamento, acesse `/questoes/simulado/` | Redireciona direto para o simulado ativo — não exibe a landing page. | ✅ (passou)

| 4.4.2 | Com simulado em andamento, tente fazer POST em `/questoes/simulado/` | Redireciona para o simulado ativo — não cria segundo simulado. | ✅ (passou)

| 4.4.3 | Após finalizar o simulado, acesse `/questoes/simulado/` | Exibe a landing page normalmente (pode iniciar novo). | ✅ (passou)

---

## BLOCO 5 — Estatísticas

**Rota:** `http://127.0.0.1:8000/estatisticas/`

### 5.1 Estado vazio

| # | Ação | Comportamento esperado |
|---|---|---|
| 5.1.1 | Acesse com usuário sem treinos | Exibe estado vazio com botão "Começar treino". Não exibe tabelas vazias. | ✅ (passou)


---

### 5.2 Com dados

> Execute após ter feito treinos em pelo menos 2 disciplinas.

| # | O que verificar | Comportamento esperado |
|---|---|---|

| 5.2.1 | Tabela de disciplinas | Ordenada do **pior aproveitamento ao melhor** (pior no topo). | ✅ (passou)

| 5.2.2 | Cores na tabela | Badge colorido de cada disciplina aparece. | ✅ (passou)

| 5.2.3 | Colunas da tabela | Disciplina, Respondidas, Acertos (colorido por faixa), Aproveitamento (barra). |✅ (passou)

| 5.2.4 | Badge basic/specific | Aparece para cada disciplina. | ✅ (passou)

| 5.2.5 | Card "Pontos Fracos" | Exibe até 5 tópicos com pior aproveitamento (mínimo 3 questões respondidas no tópico). | ⚠️ não exibe — banco sem tópicos. Pendente para quando tópicos forem importados

| 5.2.6 | Card "Pontos Fortes" | Exibe até 5 tópicos com melhor aproveitamento (mínimo 3 questões respondidas no tópico). | ⚠️ não exibe — mesmo motivo de 5.2.5

| 5.2.7 | Sem tópicos qualificados | Exibe alerta informativo nos cards (não lista vazia nem erro). | ✅ (passou) — alerta "As questões respondidas ainda não possuem tópicos classificados" aparece corretamente

| 5.2.8 | Card "Resumo" | Exibe número de disciplinas estudadas e número de tópicos estudados. | ✅ (passou) — corrigido: cabeçalho "Resumo" adicionado, mostra 13 disciplinas e 0 tópicos estudados

---

## BLOCO 6 — Responsividade

> Realize estes testes redimensionando a janela do navegador ou usando as ferramentas de dev (F12 → Toggle device toolbar).

| # | Tela | O que verificar |
|---|---|---|
| 6.1 | **Mobile (375px)** — Dashboard | Cards empilhados (2 colunas max), sem overflow horizontal, botões acessíveis. |✅ (passou)
| 6.2 | **Mobile (375px)** — Treino | Questões legíveis, alternativas tocáveis, botão "Finalizar" visível. | ✅ (passou)
| 6.3 | **Mobile (375px)** — Simulado | Cabeçalho sticky não ocupa mais que 20% da tela, questões acessíveis abaixo. | ✅ (passou)
| 6.4 | **Mobile (375px)** — Resultado | Gabarito legível, cards empilhados. |✅ (passou)
| 6.5 | **Mobile (375px)** — Navbar | Botão hambúrguer aparece; ao clicar, exibe o menu. | ✅ (passou)
| 6.6 | **Tablet (768px)** — Dashboard | 4 cards em linha (ou 2×2). | ✅ (passou)
| 6.7 | **Desktop (1280px)** — Todas as telas | Layout em colunas, sem elementos cortados. | ✅ (passou)

---

## BLOCO 7 — Fluxo completo de ponta a ponta

Execute este bloco como se fosse a Nícia usando o sistema pela primeira vez.

| # | Passo | Comportamento esperado |
|---|---|---|

| 7.1 | Abra o sistema sem estar logado | Redireciona para login. | ✅ (passou)

| 7.2 | Clique em "Cadastrar" (ou acesse `/conta/cadastro/`) | Formulário de cadastro. | ✅ (passou)

| 7.3 | Cadastre-se com e-mail e senha novos | Loga automaticamente, vai para o dashboard ou perfil. | ✅ (passou) — corrigido: agora vai para o dashboard |

| 7.4 | No perfil, defina meta diária = 20 e salve | Salva com sucesso. | ✅ (passou)

| 7.5 | Acesse o dashboard (`/`) | Exibe estado vazio. | ✅ (passou)

| 7.6 | Clique em "Questões" na navbar | Va para filtros de treino. | ✅ (passou)

| 7.7 | Selecione "Saúde Única", sem tópico, 10 questões | Cria treino e vai para resolução. |✅ (passou)

| 7.8 | Responda 7 questões e deixe 3 em branco, clique "Finalizar" | Submete com 3 puladas. |✅ (passou)

| 7.9 | Veja o resultado | Mostra ~70% (ou compatível), gabarito com cores, comentários. | ✅ (passou)

| 7.10 | Volte para o dashboard | Mostra 10 respondidas, acertos/erros corretos, streak = 1. | ✅ (passou)

| 7.11 | Acesse "Estatísticas" | Mostra Saúde Única na tabela, pontos fracos/fortes se houver tópicos qualificados. | ✅ (passou) mas nao mostras os pontos fracos e pontos fortes, foi abordad isso no descktop nos testes anteriores

| 7.12 | Clique em "Simulado" na navbar | Landing page do simulado. | ✅ (passou)

| 7.13 | Inicie o simulado | 40 questões com cronômetro. | ✅ (passou)

| 7.14 | Responda algumas questões, feche e reabra a aba | Marcações e cronômetro preservados. | ✅ (passou)

| 7.15 | Finalize o simulado | Resultado com breakdown por disciplina. | ✅ (passou)

| 7.16 | Volte para o dashboard | Métricas atualizadas com os dados do simulado também. | ✅ (passou)

| 7.17 | Faça logout | Redireciona para login. | ✅ (passou)

| 7.18 | Logue novamente | Dashboard mostra os dados da sessão anterior. | ✅ (passou) — corrigido: agora redireciona para o dashboard com dados da sessão anterior |

---

## Registro de bugs

Use a tabela abaixo para anotar os problemas encontrados durante os testes.

| # | Bloco | Passo | URL | O que aconteceu | O que deveria acontecer | Prioridade |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

**Prioridade:** 🔴 Quebra o sistema / 🟡 Comportamento errado mas não impede uso / 🟢 Visual/UX menor

---

## Checklist de cobertura

- [x] Bloco 1 — Autenticação completo
- [x] Bloco 2 — Dashboard (estado vazio + com dados)
- [x] Bloco 3 — Treino (filtros + resolução + resultado + segurança)
- [x] Bloco 4 — Simulado (criar + cronômetro + guard + resultado)
- [x] Bloco 5 — Estatísticas (vazio + com dados)
- [x] Bloco 6 — Responsividade (mobile + desktop)
- [x] Bloco 7 — Fluxo de ponta a ponta
