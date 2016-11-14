#!/bin/bash

set -a
source django_projects/pimp/.env
set +a
python virtualenv/virtualenv.py --python=python2.7 venv || exit 1 
source venv/bin/activate
pip install --no-cache-dir -r django_projects/requirements.txt || exit 1
pip install --no-cache-dir -r django_projects/requirements_frank.txt || exit 1
${PIMP_RSCRIPT_PATH} setupR.R --args --bootstrap-packrat || exit 1

rm -r PiMP PiMPDB packrat/src/*
