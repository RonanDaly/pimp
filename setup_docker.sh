#!/bin/bash

cp DockerSupport/docker.env django_projects/pimp/.env
cp DockerSupport/Procfile.docker django_projects/pimp/Procfile.docker
cp DockerSupport/initial-setup.env django_projects/pimp/initial-setup.env
exec ./setup_pimp.sh
