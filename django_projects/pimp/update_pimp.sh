#!/bin/bash

source ../../venv/bin/activate

#### To sync the database with the current version of the models

honcho run python manage.py migrate

#### To bring python packages up to date

honcho run pip install --no-cache-dir -r ../requirements.txt
honcho run pip install --no-cache-dir -r ../requirements_frank.txt
honcho run pip install --no-cache-dir -r ../requirements_dev.txt

#### To bring the R PiMP package up to date

honcho run R CMD INSTALL ../../PiMP