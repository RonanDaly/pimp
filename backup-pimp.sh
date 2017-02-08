#!/bin/bash

docker-compose run --rm --no-deps mysql bash -c 'tar cvzf /backups/mysql.tar.gz /var/lib/mysql'
docker-compose run --rm --no-deps --entrypoint 'bash -c' -u root pimp 'tar cvzf /home/pimp/backups/pimp.tar.gz /home/pimp/media'
