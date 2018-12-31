
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'respa.settings')
app = Celery('lpr_purchase')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'remove_unpaid_reservations': {
        'task': 'lpr_purchase.tasks.remove_unpaid_reservations',
        'schedule': crontab(minute='*/1')
    }
}
