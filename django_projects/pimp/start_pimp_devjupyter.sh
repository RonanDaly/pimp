#!/bin/bash

source ../../venv/bin/activate
set -a
source .env
set +a
./wait-for-it.sh -h ${PIMP_DATABASE_HOST} -p ${PIMP_DATABASE_PORT} -t 0
set -eu -o pipefail
honcho -f Procfile.devjupyter start
