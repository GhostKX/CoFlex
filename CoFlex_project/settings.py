"""
Django settings for CoFlex_project project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)


EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_BACKEND = config('EMAIL_BACKEND')

ALLOWED_HOSTS = []
AUTH_USER_MODEL = 'CoFlex_app.VerifiedUsers'
SESSION_ENGINE = "django.contrib.sessions.backends.db"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "CoFlex_app",
    "CoFlex_Booking_app",
    "CoFlex_Staff_app",
    "django_crontab",
    "django_user_agents"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",

    "django_auto_logout.middleware.auto_logout"
]

ROOT_URLCONF = "CoFlex_project.urls"

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

                "django_auto_logout.context_processors.auto_logout_client"
            ],
        },
    },
]

WSGI_APPLICATION = "CoFlex_project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE')

TIME_ZONE = config('TIME_ZONE')

USE_I18N = config('USE_I18N', cast=bool)

USE_TZ = config('USE_TZ', cast=bool)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / 'CoFlex_app/static',
    BASE_DIR / 'CoFlex_Staff_app/static'
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    'CoFlex_Staff_app.auth_backends.CustomAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'


CRONJOBS = [
    ('0 0 * * *', 'CoFlex_app.cron.delete_expired_users'),
]


FIRST_FERNET_KEY = config('FIRST_FERNET_KEY').encode()
SECOND_FERNET_KEY = config('SECOND_FERNET_KEY').encode()
THIRD_FERNET_KEY = config('THIRD_FERNET_KEY').encode()
FOURTH_FERNET_KEY = config('FOURTH_FERNET_KEY').encode()
FIFTH_FERNET_KEY = config('FIFTH_FERNET_KEY').encode()

FERNET_KEY_VERIFICATION_CODE = config('FERNET_KEY_VERIFICATION_CODE').encode()

FIRST_FERNET_KEY_LAST_FOUR_DIGITS = config('FIRST_FERNET_KEY_LAST_FOUR_DIGITS').encode()
SECOND_FERNET_KEY_LAST_FOUR_DIGITS = config('SECOND_FERNET_KEY_LAST_FOUR_DIGITS').encode()


LOCATION_ACCESS_TOKEN = config('LOCATION_ACCESS_TOKEN')

AUTO_LOGOUT = {
    'IDLE_TIME': 600,
    'SESSION_TIME': 1800,
    'MESSAGE': 'The session has expired. Please login again to continue.',
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}