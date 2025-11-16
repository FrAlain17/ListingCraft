"""
Django settings for ListingCraft project.
Base settings shared across all environments.
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR points to the root project directory (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-))tk7=1e%i-zyod!%7sv@ccafdpkt-zkbpxqn)y+2dg6kl(0&v')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])


# Application definition

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'tailwind',
    'theme',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'djstripe',

    # Local apps (will be created progressively)
    # 'apps.core',
    'apps.accounts',
    'apps.landing',
    'apps.dashboard',
    'apps.subscriptions',
    'apps.listings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
# This will be overridden in dev.py and prod.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sites framework (required for django-allauth)
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Django-allauth configuration (Updated for allauth 65.x)
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'email2*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_SESSION_REMEMBER = True
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Email configuration (will be overridden in dev.py and prod.py)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@listingcraft.online')
SERVER_EMAIL = config('SERVER_EMAIL', default='server@listingcraft.online')

# DeepSeek API Configuration
DEEPSEEK_API_KEY = config('DEEPSEEK_API_KEY', default='')
DEEPSEEK_API_URL = config('DEEPSEEK_API_URL', default='https://api.deepseek.com/v1/chat/completions')
DEEPSEEK_MODEL = config('DEEPSEEK_MODEL', default='deepseek-chat')

# Stripe Configuration
STRIPE_LIVE_MODE = config('STRIPE_LIVE_MODE', default=False, cast=bool)

# dj-stripe settings
STRIPE_LIVE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY', default='')
STRIPE_LIVE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY', default='')
STRIPE_TEST_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY', default='')
STRIPE_TEST_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY', default='')
DJSTRIPE_WEBHOOK_SECRET = config('DJSTRIPE_WEBHOOK_SECRET', default='')
DJSTRIPE_FOREIGN_KEY_TO_FIELD = 'id'
DJSTRIPE_USE_NATIVE_JSONFIELD = True

# Resend API Configuration
RESEND_API_KEY = config('RESEND_API_KEY', default='')

# Tailwind CSS Configuration
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Security settings (will be expanded in prod.py)
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
