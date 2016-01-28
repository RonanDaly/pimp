#!/bin/sh
. ../../venv/bin/activate
exec python manage.py celery worker
