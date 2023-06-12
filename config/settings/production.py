from .base import *


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

ALLOWED_HOSTS = ['.diyochat.com']
CORS_ALLOWED_ORIGINS = ['https://app.diyochat.com']

DEBUG = False

ADMIN_ENABLED = False

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True