#!/bin/bash

source ../../venv/bin/activate
set -eu -o pipefail
honcho run python manage.py collectstatic --noinput --link
