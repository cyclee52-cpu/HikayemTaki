"""
Django settings for config project.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Yerel geliştirme ortamında proje kökündeki .env dosyasını yükler.
# Canlı ortamda cPanel ortam değişkenleri kullanılır.
load_dotenv(BASE_DIR / ".env")


def get_required_env(name):
    value = os.getenv(name)

    if not value:
        raise ImproperlyConfigured(
            f"Gerekli ortam değişkeni tanımlanmamış: {name}"
        )

    return value


def get_env_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_env_list(name, default=""):
    value = os.getenv(name, default)

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


SECRET_KEY = get_required_env("DJANGO_SECRET_KEY")

DEBUG = get_env_bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = get_env_list(
    "DJANGO_ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
)

CSRF_TRUSTED_ORIGINS = get_env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
)

SESSION_COOKIE_SECURE = get_env_bool(
    "DJANGO_SESSION_COOKIE_SECURE",
    default=False,
)

CSRF_COOKIE_SECURE = get_env_bool(
    "DJANGO_CSRF_COOKIE_SECURE",
    default=False,
)

SECURE_SSL_REDIRECT = get_env_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    default=False,
)

SECURE_HSTS_SECONDS = int(
    os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0")
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = get_env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=False,
)

SECURE_HSTS_PRELOAD = get_env_bool(
    "DJANGO_SECURE_HSTS_PRELOAD",
    default=False,
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",

    "core",
    "products",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


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
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "tr-tr"

TIME_ZONE = "Europe/Istanbul"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "public" / "static"


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Production logging
LOG_DIR = BASE_DIR / "logs"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "production": {
            "format": (
                "{asctime} | {levelname} | {name} | "
                "{module}:{lineno} | {message}"
            ),
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.WatchedFileHandler",
            "filename": LOG_DIR / "django.log",
            "formatter": "production",
            "encoding": "utf-8",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.WatchedFileHandler",
            "filename": LOG_DIR / "error.log",
            "formatter": "production",
            "encoding": "utf-8",
        },
        "security_file": {
            "level": "WARNING",
            "class": "logging.handlers.WatchedFileHandler",
            "filename": LOG_DIR / "security.log",
            "formatter": "production",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "django": {
            "handlers": [
                "django_file",
                "error_file",
            ],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": [
                "security_file",
                "error_file",
            ],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
