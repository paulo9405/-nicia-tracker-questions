from decouple import config

from .base import *  # noqa: F401, F403

# Quando as variáveis PG* estão presentes (ex.: docker-compose), usa PostgreSQL.
# Caso contrário, cai no SQLite local — o fluxo padrão de desenvolvimento sem Docker.
_pgdatabase = config("PGDATABASE", default="")

if _pgdatabase:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _pgdatabase,
            "USER": config("PGUSER", default="nicia"),
            "PASSWORD": config("PGPASSWORD", default="nicia"),
            "HOST": config("PGHOST", default="localhost"),
            "PORT": config("PGPORT", default="5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# O storage com manifest (produção) exige collectstatic. Em dev, usa o storage
# simples para que o admin e qualquer {% static %} funcionem sem build prévio.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
