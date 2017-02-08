#!/bin/bash

mkdir -p django_projects/pimp
cp DockerSupport/docker.env django_projects/pimp/.env || exit 1
exec /bin/bash -c ./setup_pimp_prod.sh
