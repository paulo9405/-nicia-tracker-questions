FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# psycopg2-binary já traz a libpq embutida, mas o build de pillow precisa
# de algumas libs de imagem presentes no slim para processar avatares.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia somente os requirements primeiro → camada de cache separada das fontes.
# Se o código muda mas requirements não, o pip não reinstala nada.
COPY requirements/base.txt requirements/base.txt
COPY requirements/production.txt requirements/production.txt
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

# collectstatic exige SECRET_KEY configurada para carregar os settings.
# Usamos um valor dummy de build-time; a chave real é injetada em runtime
# via variável de ambiente, sem aparecer na imagem final.
ARG SECRET_KEY=build-time-dummy-secret-not-used-in-production
RUN ALLOWED_HOSTS=* SECRET_KEY=${SECRET_KEY} \
    python manage.py collectstatic --noinput

EXPOSE 8000

# No plano free do Render, preDeployCommand não é suportado.
# Migrations, importação e criação do admin rodam aqui, antes do gunicorn.
# Os três comandos são idempotentes: seguros de rodar em todo deploy.
CMD ["sh", "-c", "\
  python manage.py migrate --noinput && \
  python manage.py import_questions docs/15_BANCO_MESTRE_DE_QUESTOES.md && \
  python manage.py create_admin && \
  gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -"]
