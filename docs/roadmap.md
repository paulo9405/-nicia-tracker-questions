# VISÃO FINAL DO MVP

## Nome

**Nícia Track**

## Objetivo

Plataforma de preparação para concursos baseada em:

* Banco de questões
* Simulados
* Estatísticas
* Revisão de erros
* Evolução de desempenho

Usuário inicial:

* Nícia

Mas arquitetura preparada para múltiplos usuários.

---

# STACK

Backend

* Python 3.12
* Django 4.2+
* PostgreSQL

Frontend

* Bootstrap 5
* HTMX (opcional)
* JavaScript Vanilla

Infraestrutura

* Docker
* Docker Compose
* Render
* PostgreSQL Render

Qualidade

* Pytest
* Coverage
* Black
* Isort

Arquitetura

* Services Layer
* CBV para CRUD
* FBV quando fizer sentido
* Repository Pattern somente se necessário
* Clean Code

---

# FASE 1 — ARQUITETURA E MODELAGEM

## Objetivo

Definir toda a arquitetura antes de escrever código.

### Entregáveis

* Estrutura de pastas
* Apps Django
* Modelagem
* Fluxos
* Casos de uso
* Estratégia de testes
* Estratégia de deploy

---

## Prompt Fase 1

Você é um Arquiteto Django Senior.

Vamos construir um sistema chamado Nícia Track.

Objetivo:

Plataforma de preparação para concursos públicos baseada em banco de questões, simulados e acompanhamento de desempenho.

Stack obrigatória:

* Python 3.12
* Django 4.2+
* PostgreSQL
* Bootstrap 5
* Docker
* Pytest

Requisitos:

* Desktop e Mobile devem funcionar perfeitamente.
* Interface responsiva.
* Mesmo nível de experiência em ambas as plataformas.
* Sistema preparado para múltiplos usuários.

Gerar:

1. Arquitetura completa.
2. Estrutura de pastas.
3. Apps Django.
4. Fluxos principais.
5. Modelagem inicial.
6. Estratégia de Services Layer.
7. Estratégia de testes.
8. Estratégia de deploy no Render.

Não gerar código.

Apenas arquitetura detalhada.

---

# FASE 2 — MODELAGEM E BANCO

## Objetivo

Criar todas as entidades.

### Entidades

* User
* Subject
* Topic
* Question
* Quiz
* QuizQuestion
* UserAnswer
* StudySession

---

## Prompt Fase 2

Com base na arquitetura aprovada do projeto Nícia Track:

Crie a modelagem completa do banco de dados.

Objetivo:

Permitir:

* múltiplos usuários
* banco de questões
* simulados
* estatísticas
* histórico

Gerar:

1. Diagrama textual das entidades.
2. Relacionamentos.
3. Campos.
4. Índices.
5. Constraints.
6. Regras de negócio.

Não gerar código ainda.

Gerar apenas documentação técnica da modelagem.

---

# FASE 3 — IMPORTADOR DAS 800 QUESTÕES

## Objetivo

Transformar:

15_BANCO_MESTRE_DE_QUESTOES.md

em registros do PostgreSQL.

---

## Prompt Fase 3

Agora vamos construir o sistema de importação.

Origem:

15_BANCO_MESTRE_DE_QUESTOES.md

O arquivo possui:

* 800 questões
* alternativas A-D
* gabaritos
* comentários
* seções por disciplina

Sua tarefa:

Projetar o processo de importação.

Gerar:

1. Estratégia de parsing.
2. Estrutura esperada do markdown.
3. Fluxo de importação.
4. Validações.
5. Tratamento de erros.
6. Comando manage.py ideal.
7. Estratégia para reimportação sem duplicidade.

Após a documentação, gerar o código completo.

---

# FASE 4 — AUTENTICAÇÃO

## Objetivo

Criar acesso de usuários.

---

## Funcionalidades

* Cadastro
* Login
* Logout
* Perfil

---

## Prompt Fase 4

Implementar módulo de autenticação do projeto Nícia Track.

Requisitos:

* Cadastro
* Login
* Logout
* Perfil do usuário

Interface:

* Bootstrap 5
* Responsiva
* Desktop e Mobile

Seguir:

* CBV
* Services Layer
* Boas práticas Django

Gerar:

1. Código.
2. Templates.
3. URLs.
4. Testes Pytest.

---

## OBRIGAÇÃO DE DOCUMENTAÇÃO

> Parte obrigatória do processo de desenvolvimento: esta fase só pode ser considerada **concluída** após a atualização de `docs/PROJECT_EXPLAINED.md`.

Atualizar **obrigatoriamente** `docs/PROJECT_EXPLAINED.md`, acrescentando a nova fase ao final — nunca sobrescrever ou apagar fases anteriores; manter consistência visual e estrutural. A atualização deve conter:

### 1. Nova Fase Implementada
* Objetivo da fase
* Problema resolvido
* Arquivos criados
* Arquivos modificados
* Models criados
* Services criados
* Views criadas
* Templates criados
* Commands criados (se existirem)
* Testes criados
* Fluxo completo da funcionalidade
* Decisões arquiteturais
* Alternativas consideradas
* Motivos da implementação
* Benefícios obtidos

### 2. Explicação Educacional
Escrever como se estivesse ensinando um desenvolvedor júnior:
* Por que cada componente existe.
* Quando ele é executado.
* Como interage com os demais componentes.
* Como os dados percorrem o sistema.

### 3. Perguntas de Entrevista
Gerar perguntas técnicas reais sobre o que foi implementado e **responder cada uma**.

### 4. O Que Aprendi Nesta Fase
Listar conceitos de: Django, PostgreSQL, Python, arquitetura e testes.

---

# FASE 5 — BANCO DE QUESTÕES

## Objetivo

Permitir resolver questões.

---

## Funcionalidades

* Filtros
* Disciplina
* Tópico
* Quantidade

---

## Prompt Fase 5

Implementar módulo de resolução de questões.

Funcionalidades:

* Escolher disciplina.
* Escolher tópico.
* Escolher quantidade.

Opções:

* 10 questões
* 20 questões
* 50 questões

Após finalizar:

* mostrar resultado
* mostrar acertos
* mostrar erros
* mostrar percentual

Interface:

* responsiva
* desktop
* mobile

Gerar:

* models
* services
* views
* templates
* testes

---

## OBRIGAÇÃO DE DOCUMENTAÇÃO

> Parte obrigatória do processo de desenvolvimento: esta fase só pode ser considerada **concluída** após a atualização de `docs/PROJECT_EXPLAINED.md`.

Atualizar **obrigatoriamente** `docs/PROJECT_EXPLAINED.md`, acrescentando a nova fase ao final — nunca sobrescrever ou apagar fases anteriores; manter consistência visual e estrutural. A atualização deve conter:

### 1. Nova Fase Implementada
* Objetivo da fase
* Problema resolvido
* Arquivos criados
* Arquivos modificados
* Models criados
* Services criados
* Views criadas
* Templates criados
* Commands criados (se existirem)
* Testes criados
* Fluxo completo da funcionalidade
* Decisões arquiteturais
* Alternativas consideradas
* Motivos da implementação
* Benefícios obtidos

### 2. Explicação Educacional
Escrever como se estivesse ensinando um desenvolvedor júnior:
* Por que cada componente existe.
* Quando ele é executado.
* Como interage com os demais componentes.
* Como os dados percorrem o sistema.

### 3. Perguntas de Entrevista
Gerar perguntas técnicas reais sobre o que foi implementado e **responder cada uma**.

### 4. O Que Aprendi Nesta Fase
Listar conceitos de: Django, PostgreSQL, Python, arquitetura e testes.

---

# FASE 6 — DASHBOARD

## Objetivo

Mostrar evolução.

---

## Métricas

* Questões respondidas
* Acertos
* Erros
* Percentual
* Dias consecutivos

---

## Prompt Fase 6

Implementar dashboard principal do Nícia Track.

Métricas:

* total de questões respondidas
* total de acertos
* total de erros
* percentual geral
* dias consecutivos de estudo
* tempo estudado

Criar layout:

* desktop
* tablet
* mobile

Utilizar:

* cards
* progress bars
* indicadores visuais

Gerar:

* services
* views
* templates
* testes

---

## OBRIGAÇÃO DE DOCUMENTAÇÃO

> Parte obrigatória do processo de desenvolvimento: esta fase só pode ser considerada **concluída** após a atualização de `docs/PROJECT_EXPLAINED.md`.

Atualizar **obrigatoriamente** `docs/PROJECT_EXPLAINED.md`, acrescentando a nova fase ao final — nunca sobrescrever ou apagar fases anteriores; manter consistência visual e estrutural. A atualização deve conter:

### 1. Nova Fase Implementada
* Objetivo da fase
* Problema resolvido
* Arquivos criados
* Arquivos modificados
* Models criados
* Services criados
* Views criadas
* Templates criados
* Commands criados (se existirem)
* Testes criados
* Fluxo completo da funcionalidade
* Decisões arquiteturais
* Alternativas consideradas
* Motivos da implementação
* Benefícios obtidos

### 2. Explicação Educacional
Escrever como se estivesse ensinando um desenvolvedor júnior:
* Por que cada componente existe.
* Quando ele é executado.
* Como interage com os demais componentes.
* Como os dados percorrem o sistema.

### 3. Perguntas de Entrevista
Gerar perguntas técnicas reais sobre o que foi implementado e **responder cada uma**.

### 4. O Que Aprendi Nesta Fase
Listar conceitos de: Django, PostgreSQL, Python, arquitetura e testes.

---

# FASE 7 — ESTATÍSTICAS E PONTOS FRACOS

## Objetivo

Mostrar onde o usuário precisa melhorar.

---

## Prompt Fase 7

Implementar Analytics.

Funcionalidades:

* desempenho por disciplina
* desempenho por tópico
* ranking de tópicos fracos
* ranking de tópicos fortes

Exemplo:

Português 82%

Matemática 63%

Informática 91%

Criar:

* services
* consultas otimizadas
* dashboards
* testes

---

## OBRIGAÇÃO DE DOCUMENTAÇÃO

> Parte obrigatória do processo de desenvolvimento: esta fase só pode ser considerada **concluída** após a atualização de `docs/PROJECT_EXPLAINED.md`.

Atualizar **obrigatoriamente** `docs/PROJECT_EXPLAINED.md`, acrescentando a nova fase ao final — nunca sobrescrever ou apagar fases anteriores; manter consistência visual e estrutural. A atualização deve conter:

### 1. Nova Fase Implementada
* Objetivo da fase
* Problema resolvido
* Arquivos criados
* Arquivos modificados
* Models criados
* Services criados
* Views criadas
* Templates criados
* Commands criados (se existirem)
* Testes criados
* Fluxo completo da funcionalidade
* Decisões arquiteturais
* Alternativas consideradas
* Motivos da implementação
* Benefícios obtidos

### 2. Explicação Educacional
Escrever como se estivesse ensinando um desenvolvedor júnior:
* Por que cada componente existe.
* Quando ele é executado.
* Como interage com os demais componentes.
* Como os dados percorrem o sistema.

### 3. Perguntas de Entrevista
Gerar perguntas técnicas reais sobre o que foi implementado e **responder cada uma**.

### 4. O Que Aprendi Nesta Fase
Listar conceitos de: Django, PostgreSQL, Python, arquitetura e testes.

---

# FASE 8 — SIMULADOS

## Objetivo

Simular a prova real.

---

## Distribuição

* 5 Português
* 5 Matemática
* 5 Informática
* 5 Conhecimentos Gerais
* 20 Específicas

---

## Prompt Fase 8

Implementar sistema de simulados.

Formato:

40 questões.

Distribuição:

* 5 Português
* 5 Matemática
* 5 Informática
* 5 Conhecimentos Gerais
* 20 Específicas

Funcionalidades:

* cronômetro
* salvar progresso
* resultado
* correção
* revisão dos erros

Gerar:

* models
* services
* views
* templates
* testes

---

## OBRIGAÇÃO DE DOCUMENTAÇÃO

> Parte obrigatória do processo de desenvolvimento: esta fase só pode ser considerada **concluída** após a atualização de `docs/PROJECT_EXPLAINED.md`.

Atualizar **obrigatoriamente** `docs/PROJECT_EXPLAINED.md`, acrescentando a nova fase ao final — nunca sobrescrever ou apagar fases anteriores; manter consistência visual e estrutural. A atualização deve conter:

### 1. Nova Fase Implementada
* Objetivo da fase
* Problema resolvido
* Arquivos criados
* Arquivos modificados
* Models criados
* Services criados
* Views criadas
* Templates criados
* Commands criados (se existirem)
* Testes criados
* Fluxo completo da funcionalidade
* Decisões arquiteturais
* Alternativas consideradas
* Motivos da implementação
* Benefícios obtidos

### 2. Explicação Educacional
Escrever como se estivesse ensinando um desenvolvedor júnior:
* Por que cada componente existe.
* Quando ele é executado.
* Como interage com os demais componentes.
* Como os dados percorrem o sistema.

### 3. Perguntas de Entrevista
Gerar perguntas técnicas reais sobre o que foi implementado e **responder cada uma**.

### 4. O Que Aprendi Nesta Fase
Listar conceitos de: Django, PostgreSQL, Python, arquitetura e testes.

---

# FASE 9 — QUALIDADE

## Objetivo

Consolidar testes.

---

## Prompt Fase 9

Revisar todo o projeto Nícia Track.

Objetivo:

Garantir qualidade de produção.

Verificar:

* N+1 Queries
* Segurança
* Cobertura de testes
* Validações
* Responsividade
* UX Desktop
* UX Mobile

Meta:

Cobertura mínima 70%.

Gerar:

1. Auditoria técnica.
2. Melhorias necessárias.
3. Código de correção.

---

## OBRIGAÇÃO DE DOCUMENTAÇÃO

> Parte obrigatória do processo de desenvolvimento: esta fase só pode ser considerada **concluída** após a atualização de `docs/PROJECT_EXPLAINED.md`.

Atualizar **obrigatoriamente** `docs/PROJECT_EXPLAINED.md`, acrescentando a nova fase ao final — nunca sobrescrever ou apagar fases anteriores; manter consistência visual e estrutural. A atualização deve conter:

### 1. Nova Fase Implementada
* Objetivo da fase
* Problema resolvido
* Arquivos criados
* Arquivos modificados
* Models criados
* Services criados
* Views criadas
* Templates criados
* Commands criados (se existirem)
* Testes criados
* Fluxo completo da funcionalidade
* Decisões arquiteturais
* Alternativas consideradas
* Motivos da implementação
* Benefícios obtidos

### 2. Explicação Educacional
Escrever como se estivesse ensinando um desenvolvedor júnior:
* Por que cada componente existe.
* Quando ele é executado.
* Como interage com os demais componentes.
* Como os dados percorrem o sistema.

### 3. Perguntas de Entrevista
Gerar perguntas técnicas reais sobre o que foi implementado e **responder cada uma**.

### 4. O Que Aprendi Nesta Fase
Listar conceitos de: Django, PostgreSQL, Python, arquitetura e testes.

---

# FASE 10 — DEPLOY

## Objetivo

Produção.

---

## Prompt Fase 10

Preparar Nícia Track para produção.

Stack:

* Docker
* PostgreSQL
* Render

Gerar:

* Dockerfile
* docker-compose
* variáveis de ambiente
* settings de produção
* checklist de deploy
* checklist pós deploy

Objetivo:

Sistema acessível publicamente com ambiente de produção estável.

---

## OBRIGAÇÃO DE DOCUMENTAÇÃO

> Parte obrigatória do processo de desenvolvimento: esta fase só pode ser considerada **concluída** após a atualização de `docs/PROJECT_EXPLAINED.md`.

Atualizar **obrigatoriamente** `docs/PROJECT_EXPLAINED.md`, acrescentando a nova fase ao final — nunca sobrescrever ou apagar fases anteriores; manter consistência visual e estrutural. A atualização deve conter:

### 1. Nova Fase Implementada
* Objetivo da fase
* Problema resolvido
* Arquivos criados
* Arquivos modificados
* Models criados
* Services criados
* Views criadas
* Templates criados
* Commands criados (se existirem)
* Testes criados
* Fluxo completo da funcionalidade
* Decisões arquiteturais
* Alternativas consideradas
* Motivos da implementação
* Benefícios obtidos

### 2. Explicação Educacional
Escrever como se estivesse ensinando um desenvolvedor júnior:
* Por que cada componente existe.
* Quando ele é executado.
* Como interage com os demais componentes.
* Como os dados percorrem o sistema.

### 3. Perguntas de Entrevista
Gerar perguntas técnicas reais sobre o que foi implementado e **responder cada uma**.

### 4. O Que Aprendi Nesta Fase
Listar conceitos de: Django, PostgreSQL, Python, arquitetura e testes.

---

Minha recomendação: **não pule a Fase 1 e a Fase 2.** Pelo que conheço dos seus projetos, o maior ganho aqui será ter uma arquitetura bem pensada antes de começar a gerar código com Claude. Isso vai evitar retrabalho quando você chegar nas estatísticas, simulados e importação das 800 questões.

