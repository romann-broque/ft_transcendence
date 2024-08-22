"""
Django settings for transcendence_django project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-*6@dzmyjvs5+h)h1e)a!7rh*(u7%cb1g@zaad_p!a11n(k((zb"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SERV_IP = os.getenv("SERV_IP")

# Oauth2 with 42
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
OAUTH_CLIENT_UID = os.getenv("OAUTH_CLIENT_UID")
OAUTH_REDIRECT_URI = f"https://{SERV_IP}:4200/oauth-callback"
OAUTH_TOKEN_URL = "https://api.intra.42.fr/oauth/token"

ALLOWED_HOSTS = [SERV_IP, "0.0.0.0", "back-aipi", "back-user"]

# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "shared_models",
    "back_auth",
    "back_user",
    "back_game",
    "health_check",  # required
    "health_check.db",  # stock Django health checkers
    "health_check.cache",  # https://pypi.org/project/django-health-check/
    "health_check.storage",
    "health_check.contrib.migrations",
    "django_extensions",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "transcendence_django.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "transcendence_django.wsgi.application"
ASGI_APPLICATION = "transcendence_django.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", ""),
        "USER": os.getenv("POSTGRES_USER", ""),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": "db",  # localhost
        "PORT": "5432",
    }
}

AUTH_USER_MODEL = "shared_models.CustomUser"

CSRF_TRUSTED_ORIGINS = [
    f"https://{SERV_IP}:4200",
]
CORS_ALLOWED_ORIGINS = [
    f"https://{SERV_IP}:4200",
]
CORS_ALLOW_CREDENTIALS = True
AUTHENTICATION_BACKENDS = ["back_auth.backends.EmailOrUsernameModelBackend"]
CORS_ALLOW_HEADERS = [
    "CONTENT-TYPE",
    "X-CSRFToken",
]
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

print("Database settings:")
print("Name:", DATABASES["default"]["NAME"])
print("User:", DATABASES["default"]["USER"])
print("Password:", DATABASES["default"]["PASSWORD"])
print("Host:", DATABASES["default"]["HOST"])
print("Port:", DATABASES["default"]["PORT"])

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Minio settings for avatar file upload
MINIO_STORAGE_ENDPOINT = "https://127.0.0.1:9000"
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_STORAGE_USE_HTTPS = True
MINIO_STORAGE_MEDIA_BUCKET_NAME = "avatars"
DEFAULT_AVATAR_PATH = "avatars/default_avatar.jpg"
