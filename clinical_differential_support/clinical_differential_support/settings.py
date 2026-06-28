"""Settings for the clinical differential support MVP."""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_csv(name: str) -> list[str]:
    value = os.environ.get(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_int(name: str, default: int = 0) -> int:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as error:
        raise ImproperlyConfigured(f"{name} must be an integer.") from error


IS_RENDER = _env_bool("RENDER")
DEBUG = _env_bool("DJANGO_DEBUG", default=not IS_RENDER)

_secret_key = os.environ.get("DJANGO_SECRET_KEY") or os.environ.get("SECRET_KEY")
if not _secret_key and not DEBUG:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG=0.")
SECRET_KEY = _secret_key or "local-mvp-not-for-production"

ALLOWED_HOSTS = _env_csv("DJANGO_ALLOWED_HOSTS") or (
    ["127.0.0.1", "localhost"] if DEBUG else []
)
_render_external_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if _render_external_hostname and _render_external_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_external_hostname)
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS or RENDER_EXTERNAL_HOSTNAME must be set when DJANGO_DEBUG=0."
    )

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cds_core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "clinical_differential_support.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "clinical_differential_support.wsgi.application"

_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            ssl_require=_env_bool("DJANGO_DB_SSL_REQUIRE", default=IS_RENDER),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

if IS_RENDER and _database_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cds_status_cache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "clinical-differential-support",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Taipei"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
if not DEBUG:
    STORAGES["staticfiles"][
        "BACKEND"
    ] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CSRF_TRUSTED_ORIGINS = _env_csv("DJANGO_CSRF_TRUSTED_ORIGINS")
if _render_external_hostname:
    render_origin = f"https://{_render_external_hostname}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = _env_bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = _env_bool("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = _env_bool("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_HSTS_SECONDS = _env_int(
    "DJANGO_SECURE_HSTS_SECONDS",
    default=0 if DEBUG else 31536000,
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=False,
)
SECURE_HSTS_PRELOAD = _env_bool("DJANGO_SECURE_HSTS_PRELOAD", default=False)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
