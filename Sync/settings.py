"""
Configurações do projeto SyncWeb (Django 6.1).

Tudo que muda entre o seu computador e o servidor (chave secreta, DEBUG,
domínio, e-mail, WhatsApp...) vem do arquivo .env na raiz do projeto.
Veja o modelo em .env.example.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# lê o arquivo .env (se existir) e joga os valores nas variáveis de ambiente
load_dotenv(BASE_DIR / ".env")


def env(nome, padrao=""):
    return os.environ.get(nome, padrao)


def env_bool(nome, padrao=False):
    return env(nome, str(padrao)).strip().lower() in {"1", "true", "sim", "yes", "on"}


def env_lista(nome, padrao=""):
    return [item.strip() for item in env(nome, padrao).split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Segurança básica
# ---------------------------------------------------------------------------
DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = env("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # só para desenvolvimento: em produção a chave é obrigatória no .env
        SECRET_KEY = "dev-inseguro-troque-no-env"
    else:
        raise RuntimeError("Defina DJANGO_SECRET_KEY no arquivo .env")

ALLOWED_HOSTS = env_lista("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
# ex.: https://www.syncweb.com.br (necessário para formulários em produção com HTTPS)
CSRF_TRUSTED_ORIGINS = env_lista("DJANGO_CSRF_TRUSTED_ORIGINS")


# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",  # runserver usa o WhiteNoise (igual à produção)
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # apps do projeto
    "core",  # páginas, layout base, SEO (sitemap, robots), 404
    "conteudo",  # planos, dúvidas, projetos e depoimentos editáveis no admin
    "contato",  # formulário de orçamento e pedidos recebidos
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve CSS/JS/imagens em produção
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Sync.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",  # dados da empresa em todos os templates
            ],
        },
    },
]

WSGI_APPLICATION = "Sync.wsgi.application"


# ---------------------------------------------------------------------------
# Banco de dados (SQLite: um arquivo, suficiente para um site institucional)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Senhas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# Idioma e fuso horário
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Arquivos estáticos (CSS, JS, fontes, imagens do layout) e de mídia (uploads)
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # destino do "collectstatic" em produção

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # em produção: arquivos comprimidos e com nome versionado (cache longo e seguro)
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"  # prints dos projetos enviados pelo admin


# ---------------------------------------------------------------------------
# E-mail (aviso de novo pedido de orçamento)
# Em desenvolvimento os e-mails aparecem no terminal. Em produção, preencha
# EMAIL_HOST etc. no .env para enviar de verdade (SMTP).
# ---------------------------------------------------------------------------
if env("EMAIL_HOST"):
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": env("EMAIL_HOST"),
                "port": int(env("EMAIL_PORT", "587")),
                "username": env("EMAIL_HOST_USER"),
                "password": env("EMAIL_HOST_PASSWORD"),
                "use_tls": env_bool("EMAIL_USE_TLS", True),
                "timeout": 10,
            },
        },
    }
else:
    MAILERS = {
        "default": {"BACKEND": "django.core.mail.backends.console.EmailBackend"},
    }

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "SyncWeb <nao-responda@localhost>")
# quem recebe o aviso de novo pedido (pode ser mais de um, separados por vírgula)
CONTATO_DESTINATARIOS = env_lista("CONTATO_DESTINATARIOS")


# ---------------------------------------------------------------------------
# Dados da empresa exibidos no site (core/context_processors.py)
# ---------------------------------------------------------------------------
EMPRESA = {
    "nome": "SyncWeb Solutions",
    "whatsapp": "".join(c for c in env("EMPRESA_WHATSAPP") if c.isdigit()),
    "email": env("EMPRESA_EMAIL"),
    "cnpj": env("EMPRESA_CNPJ"),
    "razao_social": env("EMPRESA_RAZAO_SOCIAL"),
    "horario": env("EMPRESA_HORARIO", "Segunda a sexta, das 9h às 18h"),
    "instagram": env("EMPRESA_INSTAGRAM"),
    "linkedin": env("EMPRESA_LINKEDIN"),
}

# script de estatísticas sem cookies (opcional), ex.: seudominio.com.br
PLAUSIBLE_DOMAIN = env("PLAUSIBLE_DOMAIN")


# ---------------------------------------------------------------------------
# Segurança em produção (só vale com DEBUG desligado)
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(env("DJANGO_HSTS_SECONDS", "0"))  # suba para 31536000 depois de testar o HTTPS
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
