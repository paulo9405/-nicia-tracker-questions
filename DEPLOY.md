# Guia de Deploy — Nícia Track no Render

---

## Antes de começar

Confirme que o código está no GitHub:

```bash
git push origin main
```

---

## PARTE 1 — Criar o Blueprint no Render

### 1.1 Acesse o Render

Entre em **render.com** com sua conta.

### 1.2 Novo Blueprint

No dashboard clique em **New → Blueprint**.

### 1.3 Conecte o repositório

- Clique em **Connect account** (se ainda não autorizou o GitHub) ou selecione o GitHub
- Na lista de repositórios, encontre **consurso-nicia** (ou **-nicia-tracker-questions**) e clique em **Connect**

O Render vai ler o arquivo `render.yaml` e mostrar um preview com:

```
✔ nicia-track-db   (PostgreSQL — Free)
✔ nicia-track      (Web Service — Free)
```

> **Observação:** se já tiver um banco PostgreSQL gratuito em outra aplicação,
> o Render pode reclamar de limite. Nesse caso, use a Opção B no final deste guia.

---

## PARTE 2 — Preencher as variáveis de ambiente

Ainda na tela de preview, role para baixo até ver a seção de **Environment Variables** do serviço `nicia-track`.

Você vai ver uma tabela com várias variáveis. A maioria já está preenchida automaticamente. Você precisa preencher **somente estas:**

---

### ADMIN_EMAIL

> Login do painel de administração (/admin/)

**Campo:** `ADMIN_EMAIL`
**Valor:** seu e-mail (ex: paulo@email.com)

---

### ADMIN_PASSWORD

> Senha do painel de administração

**Campo:** `ADMIN_PASSWORD`
**Valor:** uma senha forte (ex: MinhaS3nh@Forte!)

---

### CSRF_TRUSTED_ORIGINS

> Já vem preenchido com `https://nicia-track.onrender.com`
> Deixe assim por enquanto — você vai confirmar ou corrigir no Passo 4

---

Não mexa nas outras variáveis (SECRET_KEY, PGHOST, PGPASSWORD, etc.).
O Render preenche essas automaticamente.

---

## PARTE 3 — Aplicar e aguardar

### 3.1 Dê um nome ao Blueprint e clique em Apply

Coloque qualquer nome no campo **Blueprint Name** (ex: `nicia-track`) e clique em **Apply**.

O Render vai executar tudo automaticamente nesta ordem:

```
[1/3] Criando banco PostgreSQL...          (~1 min)
[2/3] Construindo imagem Docker...         (~4 min)
      - instala dependências Python
      - gera os arquivos estáticos (collectstatic)
[3/3] Iniciando o container...             (~2 min)
      - migrate          → cria todas as tabelas no banco
      - import_questions → importa as 800 questões do Markdown
      - create_admin     → cria o superusuário com seu e-mail e senha
      - gunicorn         → sobe o servidor web
```

> **Importante:** no plano free do Render, `preDeployCommand` não é suportado.
> Por isso migrate, import_questions e create_admin rodam dentro do próprio
> container na inicialização, antes do gunicorn subir. É mais lento na primeira
> vez (~2 min extras), mas funciona perfeitamente.

### 3.2 Acompanhe os logs

Na página do serviço `nicia-track`, clique na aba **Logs**.

O deploy terminou com sucesso quando aparecer algo como:

```
Criadas: 800 | Atualizadas: 0 | Inalteradas: 0 | Disciplinas: 13
Superusuário paulo@email.com criado com sucesso.
[INFO] Booting worker with pid: ...
```

---

## PARTE 4 — Pegar a URL e corrigir CSRF

### 4.1 Copie a URL do serviço

No topo da página do serviço `nicia-track` você vai ver a URL, exemplo:

```
https://nicia-track.onrender.com
```

> ⚠️ Se o nome `nicia-track` já estava em uso por outra pessoa no Render,
> a URL pode ser diferente, como `https://nicia-track-a1b2.onrender.com`.
> Use a URL que o Render mostrar, não invente.

### 4.2 Atualize CSRF_TRUSTED_ORIGINS

1. No serviço `nicia-track`, clique na aba **Environment**
2. Encontre a variável `CSRF_TRUSTED_ORIGINS`
3. Clique no lápis (editar) ao lado dela
4. Troque o valor pela URL real:

```
https://nicia-track.onrender.com
```

   (use a URL que você copiou no passo 4.1)

5. Clique em **Save Changes**

### 4.3 Faça um novo deploy

Após salvar, o Render vai perguntar se quer redesployar. Clique em:

**Manual Deploy → Deploy latest commit**

Aguarde o deploy terminar (~2 min).

> Neste segundo deploy os comandos rodam de novo, mas são seguros:
> - `migrate` → não faz nada (tabelas já existem)
> - `import_questions` → vê que as 800 questões não mudaram, não duplica nada
> - `create_admin` → vê que o usuário já existe, não faz nada
> - `gunicorn` → sobe normalmente

---

## PARTE 5 — Verificar que está funcionando

### 5.1 Abra a URL no navegador

Deve aparecer a tela de login do Nícia Track.

### 5.2 Faça login

- **E-mail:** o que você colocou em `ADMIN_EMAIL`
- **Senha:** o que você colocou em `ADMIN_PASSWORD`

### 5.3 Verifique o dashboard

O dashboard deve mostrar **0 questões respondidas** (usuário novo, normal).

### 5.4 Verifique o banco de questões

- Clique em **Questões** na navbar
- O select de disciplinas deve mostrar as 13 disciplinas (Saúde Única, Português, etc.)
- Isso confirma que as 800 questões foram importadas com sucesso

### 5.5 Verifique o admin

Acesse `https://sua-url.onrender.com/admin/` e faça login.
Deve aparecer o painel com Questions, Subjects, Users, etc.

---

## Solução de problemas

### Formulário retorna erro 403

**Causa:** `CSRF_TRUSTED_ORIGINS` não corresponde à URL real do serviço.

**Solução:** repita o Passo 4 com a URL correta.

---

### Tela branca ou erro 500

**Causa:** provavelmente alguma variável de ambiente faltando ou errada.

**Solução:**
1. Vá em **Logs** e leia a mensagem de erro
2. Vá em **Environment** e confira se `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `CSRF_TRUSTED_ORIGINS` estão preenchidos

---

### Select de disciplinas aparece vazio

**Causa:** `import_questions` pode ter falhado na inicialização.

**Solução:**
1. Vá em **Logs** e procure pela linha `Criadas: 800`
2. Se não aparecer, faça um **Manual Deploy** e aguarde

---

### Container demora muito para subir (> 5 min)

**Causa:** na primeira inicialização, migrate + import_questions rodam antes do gunicorn.
Isso é normal e ocorre apenas no primeiro deploy ou quando o banco é recriado.

**Solução:** aguarde. Acompanhe em **Logs**.

---

### Primeiro acesso demora 30–60 segundos

**Normal.** O plano free do Render "dorme" o serviço após 15 minutos sem requisições.
A primeira requisição acorda o servidor. Após isso, o sistema responde normalmente.

---

## Informações importantes sobre o plano Free

| Item | Detalhe |
|---|---|
| **Spin-down** | Serviço dorme após 15 min sem uso. Primeira requisição demora ~30–60s. |
| **Banco expira** | PostgreSQL gratuito é deletado após 90 dias sem atividade |
| **Se o banco expirar** | As 800 questões são reimportadas automaticamente no próximo deploy. O superusuário também é recriado automaticamente (as env vars continuam salvas no Render). |
| **Avatares** | Imagens de avatar enviadas pelos usuários são perdidas no redeploy (limitação do Free). |
| **preDeployCommand** | Não suportado no free — migrate/import/create_admin rodam no CMD do container. |

---

## Resumo das variáveis que você precisa preencher

| Variável | Onde preencher | Exemplo |
|---|---|---|
| `ADMIN_EMAIL` | Tela de Blueprint (Parte 2) | paulo@email.com |
| `ADMIN_PASSWORD` | Tela de Blueprint (Parte 2) | MinhaS3nh@Forte! |
| `CSRF_TRUSTED_ORIGINS` | Environment após primeiro deploy (Parte 4) | https://nicia-track.onrender.com |

---

## Opção B — Criar na mão (se Blueprint reclamar de limite de banco gratuito)

Se o Render não deixar criar um segundo banco gratuito pelo Blueprint:

**1. Criar o banco** → **New → Postgres**
- Name: `nicia-track-db`
- Plan: Free
- Anote: Host, Port, Database, Username, Password

**2. Criar o serviço web** → **New → Web Service**
- Repositório: selecione o repo do projeto
- **Runtime:** Docker ← obrigatório
- Branch: main
- Plan: Free

**3. Adicionar as variáveis de ambiente** (aba Environment do serviço):

| Variável | Valor |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | clique em **Generate** |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://<nome-do-servico>.onrender.com` (atualiza depois) |
| `ADMIN_EMAIL` | seu e-mail |
| `ADMIN_PASSWORD` | senha forte |
| `PGHOST` | host do banco (copiado no passo 1) |
| `PGPORT` | `5432` |
| `PGDATABASE` | nome do banco (copiado no passo 1) |
| `PGUSER` | usuário do banco (copiado no passo 1) |
| `PGPASSWORD` | senha do banco (copiado no passo 1) |

**4.** Salve e aguarde o deploy. Depois siga a partir da **Parte 4** deste guia.
