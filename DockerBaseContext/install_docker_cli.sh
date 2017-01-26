#!/bin/bash

DOCKER_TAR_FILE=docker-1.13.0.tgz

cd /tmp
wget https://get.docker.com/builds/Linux/x86_64/$DOCKER_TAR_FILE
tar xzvf $DOCKER_TAR_FILE
cp docker/docker /usr/local/bin
rm -r $DOCKER_TAR_FILE docker
