#!/bin/bash

echo "NOTICE: Get static files for serving"
./manage.py collectstatic --no-input

echo "NOTICE: Start Celery beat"
# celery --app=lpr_purchase.celery:app beat -f /tmp/celery_beat.log --loglevel=INFO --detach

echo "NOTICE: Start Celery worker"
# celery --app=lpr_purchase.celery:app worker -f /tmp/celery_worker.log --loglevel=INFO --detach

echo "NOTICE: Start the gunicorn web server"
gunicorn --access-logfile - --error-logfile - --log-level info -b 0.0.0.0:8000 deploy.wsgi
