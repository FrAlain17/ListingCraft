"""
Production settings for ListingCraft.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Update this with your actual domain
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='listingcraft.online,www.listingcraft.online',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Database - PostgreSQL for production
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='listingcraft'),
        'USER': config('DB_USER', default='listingcraft'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# Email backend - Resend via django-anymail
EMAIL_BACKEND = 'anymail.backends.resend.EmailBackend'
ANYMAIL = {
    "RESEND_API_KEY": config('RESEND_API_KEY'),
}

# Security settings for production
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Additional security headers
SECURE_REFERRER_POLICY = 'same-origin'

# Session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# CSRF security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False  # Use cookie-based CSRF

# Password validation - stricter in production
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://listingcraft.online',
    'https://www.listingcraft.online',
]

# Stripe live mode
STRIPE_LIVE_MODE = True
DJSTRIPE_WEBHOOK_SECRET = config('DJSTRIPE_WEBHOOK_SECRET')

# Static files - Use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Cache configuration - Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# Session storage - Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
