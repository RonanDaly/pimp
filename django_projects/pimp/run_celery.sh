#!/bin/sh
. ../../venv/bin/activate
if [ -z ${PIMP_CELERY_CONCURRENCY+x} ]; then
	exec python manage.py celery worker;
else
	exec python manage.py celery worker --concurrency ${PIMP_CELERY_CONCURRENCY};
fi
