from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import logging

# Load environment variables from .env
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv('SECRET_KEY', 'replace-me-with-a-secure-secret-in-prod')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')

# ALLOWED_HOSTS
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'app.apps.AppConfig',
    'django_celery_beat',
    'django_celery_results',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS (frontend origins)
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE

default_cors = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://premorning-unadvantaged-melvin.ngrok-free.dev",
    "https://app.botpress.cloud",
]

cors_env = os.getenv('CORS_ALLOWED_ORIGINS')
CORS_ALLOWED_ORIGINS = [c.strip() for c in cors_env.split(',')] if cors_env else default_cors

# CSRF trusted origins - include Render domain by default
default_csrf = [
    "https://koyanardzshop.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
csrf_env = os.getenv('CSRF_TRUSTED_ORIGINS')
CSRF_TRUSTED_ORIGINS = [c.strip() for c in csrf_env.split(',')] if csrf_env else default_csrf

# CSRF Cookie Settings
CSRF_COOKIE_HTTPONLY = False  # Allow template tag to work
CSRF_COOKIE_AGE = 31449600  # One year
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF

ROOT_URLCONF = 'BuynSell.urls'

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
                'app.context_processors.favorites_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'BuynSell.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override if DATABASE_URL is provided (Postgres on Render)
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
# Accept either 'postgresql://' or 'postgres://' prefixes (Render may provide either)
if DATABASE_URL and (DATABASE_URL.startswith('postgresql://') or DATABASE_URL.startswith('postgres://')):
    # Parse the DATABASE_URL environment variable (e.g. provided by Render)
    # and ensure SSL is required in production (when DEBUG is False).
    db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    if not DEBUG:
        # Ensure SSL for production Postgres (Render provides a secure endpoint)
        # dj-database-url doesn't always set sslmode; set it explicitly.
        options = db_config.get('OPTIONS', {})
        # Use 'require' to enforce SSL/TLS
        options.setdefault('sslmode', 'require')
        db_config['OPTIONS'] = options
    DATABASES = {'default': db_config}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Authentication URLs
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Celery config
CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Asia/Manila')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'sqla+sqlite:///celery_messages.sqlite')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'django-db')

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'koyanardzshop@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'cmbfctwxszqwjqwe')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
# Timeout (seconds) for SMTP connection attempts. Prevents blocking the worker
# indefinitely when the SMTP host is unreachable (which caused Gunicorn worker
# timeouts and process exits in production). Can be overridden via env var.
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', 10))

# SendGrid (via Anymail) support - Render-friendly email service
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '').strip()
if SENDGRID_API_KEY:
    # Ensure Anymail is available for SendGrid
    if 'anymail' not in INSTALLED_APPS:
        INSTALLED_APPS.append('anymail')
    EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
    ANYMAIL = {
        'SENDGRID_API_KEY': SENDGRID_API_KEY,
    }
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@koyanardzshop.com')
else:
    # Fallback to Gmail for local development (requires app-specific password)
    # On Render production, set SENDGRID_API_KEY environment variable instead
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'app.CustomUser'

# Ensure DEFAULT_FROM_EMAIL is a valid email address. If the environment
# provides an invalid value (for example missing the '@'), fall back to
# `EMAIL_HOST_USER` to avoid sending errors such as MailerSend MS42208.
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '').strip()
if not DEFAULT_FROM_EMAIL or '@' not in DEFAULT_FROM_EMAIL:
    logger = logging.getLogger(__name__)
    if DEFAULT_FROM_EMAIL:
        logger.warning("Invalid DEFAULT_FROM_EMAIL '%s' — falling back to EMAIL_HOST_USER", DEFAULT_FROM_EMAIL)
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Dynamic SITE_ID based on environment - will be determined at runtime
# SITE_ID is only used as a fallback; allauth prefers getting site from request
SITE_ID = 1

# Django-allauth settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', ''),
            'key': ''
        }
    }
}

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Google signup: no email verification
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'   # Normal signup: email verification required
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Allauth adapter settings - use custom adapter to handle multi-site deployments
SOCIALACCOUNT_ADAPTER = 'app.socialadapter.CustomSocialAccountAdapter'
SOCIALACCOUNT_STORE_TOKENS = True

# Production security
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', 2592000))  # 30 days
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ('1', 'true', 'yes')
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('1', 'true', 'yes')

# Basic logging: ensure errors are visible in host logs (stdout/stderr)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}
