from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("PGDATABASE", default="nicia_track"),
        "USER": config("PGUSER", default="nicia"),
        "PASSWORD": config("PGPASSWORD", default=""),
        "HOST": config("PGHOST", default="localhost"),
        "PORT": config("PGPORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

# Atrás do proxy reverso do Render, o Django só sabe que a requisição
# original era HTTPS pelo header X-Forwarded-Proto. Sem isto,
# SECURE_SSL_REDIRECT entra em loop infinito de redirecionamento.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Django 4.x exige origins confiáveis para aceitar POST sob HTTPS.
# Sem isto, todos os formulários falham com 403 CSRF em produção.
# Ex.: CSRF_TRUSTED_ORIGINS=https://nicia-track.onrender.com
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
    if origin.strip()
]
