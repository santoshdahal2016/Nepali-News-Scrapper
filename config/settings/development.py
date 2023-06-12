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
        'level': 'DEBUG',
    },
}

ALLOWED_HOSTS = ['127.0.0.1', '127.0.0.1:8000', 'localhost', '0.0.0.0', '0.0.0.0:8000', 'diyo.ai', 'goluhospital.diyo.ai']

DEBUG = True

ADMIN_ENABLED = True

CORS_ALLOW_ALL_ORIGINS = True