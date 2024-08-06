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

SERV_IP = os.getenv("SERV_IP", "")

ALLOWED_HOSTS = [SERV_IP, "0.0.0.0"]

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
    f"https://{SERV_IP}:8001",
]
CORS_ALLOWED_ORIGINS = [
    f"https://{SERV_IP}:4200",
    f"https://{SERV_IP}:8001",
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

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'debug.log'),
#         },
#     },
#     'root': {
#         'handlers': ['console', 'file'],
#         'level': 'DEBUG',
#     },
# }
