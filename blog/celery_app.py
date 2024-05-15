import os

# import time
#
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bike_blog.settings')

app = Celery('bike_blog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True


