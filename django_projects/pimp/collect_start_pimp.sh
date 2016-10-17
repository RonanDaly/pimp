#!/bin/bash

source ../../venv/bin/activate
honcho run python manage.py collectstatic --noinput --link
exec ./start_pimp.sh
