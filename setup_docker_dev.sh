#!/bin/bash

cp DockerSupport/docker.env django_projects/pimp/.env || exit 1
exec /bin/bash -c ./setup_pimp_dev.sh
