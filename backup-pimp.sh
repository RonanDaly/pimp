#!/bin/bash

version=${1:-backup}
docker-compose run --rm --no-deps mysql bash -c "tar cvzf /backups/pimp-${version}-mysql.tar.gz /var/lib/mysql"
#docker-compose run --rm --no-deps --entrypoint 'bash -c' -u root pimp "tar cvzf /home/pimp/backups/pimp-${version}-media.tar.gz /home/pimp/media"
