import os

from celery import Celery
from environs import Env

env = Env()
env.read_env()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

if env('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = env('DJANGO_SETTINGS_MODULE')


app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

