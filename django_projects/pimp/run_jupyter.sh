#!/bin/sh

. ../../venv/bin/activate
exec python manage.py shell_plus --notebook
