# Deploy — Nícia Track

## PASSO 1 — Banco de dados (Neon)

1. Acesse **neon.tech** e crie uma conta gratuita
2. Crie um projeto (o nome não importa)
3. Vá em **Connection Details** e anote os 5 valores:

```
Host:     ep-xxxx.us-east-2.aws.neon.tech
Database: neondb
User:     neondb_owner
Password: xxxxxxxxxxxx
Port:     5432
```

---

## PASSO 2 — Web Service (Render)

1. Acesse **render.com** → **New → Web Service**
2. Conecte o repositório **-nicia-tracker-questions**
3. Configure:
   - **Runtime:** Docker
   - **Branch:** main
   - **Plan:** Free

---

## PASSO 3 — Variáveis de ambiente

Na mesma tela de criação, em **Environment Variables**, adicione:

| Variável | Valor |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | clique em **Generate** |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://nicia-track.onrender.com` ⚠️ corrija depois |
| `ADMIN_EMAIL` | seu e-mail (login do /admin/) |
| `ADMIN_PASSWORD` | senha forte |
| `PGHOST` | Host do Neon |
| `PGPORT` | `5432` |
| `PGDATABASE` | Database do Neon |
| `PGUSER` | User do Neon |
| `PGPASSWORD` | Password do Neon |

Clique em **Create Web Service**.

---

## PASSO 4 — Aguardar o deploy

Acompanhe na aba **Logs**. O deploy terminou quando aparecer:

```
Criadas: 800 | Atualizadas: 0 | Inalteradas: 0 | Disciplinas: 13
Superusuário criado com sucesso.
[INFO] Booting worker with pid: ...
```

---

## PASSO 5 — Corrigir CSRF

1. Copie a URL do serviço no topo da página (ex: `https://nicia-track.onrender.com`)
2. Vá em **Environment** → edite `CSRF_TRUSTED_ORIGINS` com a URL real
3. Clique em **Save Changes** → **Manual Deploy → Deploy latest commit**

---

## PASSO 6 — Testar

- Acesse a URL → deve aparecer a tela de login
- Faça login com `ADMIN_EMAIL` e `ADMIN_PASSWORD`
- Clique em **Questões** → deve listar as 13 disciplinas
- Acesse `/admin/` → painel de curadoria

---

## Problemas comuns

**403 nos formulários** → `CSRF_TRUSTED_ORIGINS` errado. Refaça o Passo 5.

**Disciplinas vazias** → `import_questions` falhou. Veja os Logs e faça um Manual Deploy.

**Primeiro acesso lento (~30s)** → normal. O serviço hiberna após 15 min sem uso.
