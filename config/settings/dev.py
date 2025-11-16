"""
Development settings for ListingCraft.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend - console output for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar (will be added later)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
# INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Disable HTTPS redirects in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Stripe test mode
STRIPE_LIVE_MODE = False
DJSTRIPE_WEBHOOK_SECRET = config('DJSTRIPE_WEBHOOK_SECRET', default='')
