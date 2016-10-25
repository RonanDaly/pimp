#!/bin/bash

set -a
source django_projects/pimp/.env
set +a
python virtualenv/virtualenv.py --python=python2.7 venv
source venv/bin/activate
pip install --no-cache-dir -r django_projects/requirements.txt
pip install --no-cache-dir -r django_projects/requirements_frank.txt
${PIMP_RSCRIPT_PATH} setupR.R --args --bootstrap-packrat

rm -r PiMP PiMPDB packrat/src/*
