#!/bin/bash

cp DockerSupport/docker.env django_projects/pimp/.env || exit 1
cp DockerSupport/Procfile.docker.dev django_projects/pimp/Procfile.docker || exit 1
cp DockerSupport/Procfile.docker.jupyter django_projects/pimp/Procfile.jupyter || exit 1
exec /bin/bash -c ./setup_pimp_dev.sh
