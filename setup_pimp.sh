#!/bin/bash

set -a
source django_projects/pimp/.env
set +a
python virtualenv/virtualenv.py --python=python2.7 venv
source venv/bin/activate
pip install -r django_projects/requirements.txt
pip install -r django_projects/requirements_frank.txt
${PIMP_RSCRIPT_PATH} setupR.R --args --bootstrap-packrat
cd django_projects/pimp
# Database needs to be available from this point
honcho run python manage.py migrate
honcho run python setupInitialUser.py
honcho run python manage.py collectstatic --noinput --link
honcho -f Procfile.docker export supervisord ../.. -u pimp --template-dir=../../python_support/honcho
