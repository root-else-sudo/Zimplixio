from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

INSTALLED_APPS = [
    'core',
    'pages',
    'showcase',
    'metrics',
    'booking',
    'framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ContentSecurityPolicyMiddleware',
]

ROOT_URLCONF = 'Zimplixio_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Zimplixio_site.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
}

# Persistent database connections. Django's default (CONN_MAX_AGE=0) opens and tears
# down a connection on every single request; the handshake used to cost ~800ms per
# request and dominated response time. Do not remove — see docs/GOTCHAS.md.
# CONN_HEALTH_CHECKS revalidates a pooled connection before reuse, so a stale socket
# surfaces as a transparent reconnect instead of a 500.
DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=600)
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
# Display timezone. Storage stays UTC (USE_TZ=True) -- this only controls how
# datetimes are rendered and how datetime form input is interpreted. It is
# Eastern because that is where the business operates and because the admin
# shows aware `created_at`/`submitted_at` beside naive `requested_time`
# values that are already Eastern; leaving this as UTC put two timezones five
# hours apart in the same table row. Keep in sync with BOOKING_TIMEZONE below.
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@zimplixio.com')
LEAD_NOTIFICATION_EMAIL = env('LEAD_NOTIFICATION_EMAIL', default='')
ZOOM_MEETING_URL = env('ZOOM_MEETING_URL', default='')
SITE_URL = env('SITE_URL', default='http://localhost:8000')
# The timezone slot times are published in. Deliberately a separate setting
# from TIME_ZONE (display) even though both are Eastern today: booking
# availability is a business rule, not a rendering preference.
BOOKING_TIMEZONE = 'America/New_York'
# Length of a discovery call. Read by both the email templates and the
# calendar invite, so the advertised duration and the booked block cannot
# drift apart.
BOOKING_DURATION_MINUTES = 30
# Shown as the host's name on the calendar invitation's guest list. The
# organizer is the Zimplixio brand (team@), the host is the person the
# visitor is actually meeting -- they must differ, or the guest list
# reads 'Zimplixio, Zimplixio'.
BOOKING_HOST_NAME = 'Joe Ugalde'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
