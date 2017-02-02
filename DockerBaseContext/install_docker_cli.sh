#!/bin/bash

DOCKER_TAR_FILE=docker-1.13.0.tgz

# Installing docker
cd /tmp
wget https://get.docker.com/builds/Linux/x86_64/$DOCKER_TAR_FILE
tar xzvf $DOCKER_TAR_FILE
cp docker/docker /usr/local/bin
rm -r $DOCKER_TAR_FILE docker

# Installing docker-compose
wget https://github.com/docker/compose/releases/download/1.10.0/docker-compose-`uname -s`-`uname -m` -O /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
