#!/bin/sh
. ../../venv/bin/activate
exec python manage.py runserver 

# (testing for Eclipse settings) --settings=pimp.settings_dev
