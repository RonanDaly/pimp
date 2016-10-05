#!/bin/bash

cp DockerContext/docker.env django_projects/pimp/.env
cp DockerContext/Procfile.docker django_projects/pimp/Procfile.docker
set -a
source DockerContext/initial-setup.env
set +a
exec setup_pimp.sh
