#!/bin/bash

version=${1:-backup}
docker-compose run --rm --no-deps mysql bash -c "cd / && tar xvzf /backups/pimp-${version}-mysql.tar.gz"
#docker-compose run --rm --no-deps --entrypoint 'bash -c' pimp "cd / && tar xvzf /home/pimp/backups/pimp-${version}-media.tar.gz"
