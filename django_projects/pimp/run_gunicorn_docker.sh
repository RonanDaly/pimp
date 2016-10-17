#!/bin/sh
. ../../venv/bin/activate
#PIMP_IP_ADDRESS=$(getent hosts ${HOSTNAME} | awk '{ print $1 }')
exec gunicorn pimp.wsgi:application -w 5 --user=pimp --group=pimp --settings=settings --bind ${HOSTNAME}:8000 --log-level=${PIMP_LOG_LEVEL} --timeout=2000 --access-logfile -
