#!/bin/bash

docker-compose run --rm --no-deps mysql bash -c 'cd / && tar xvzf /backups/mysql.tar.gz'
docker-compose run --rm --no-deps --entrypoint='bash -c' pimp 'cd / && tar xvzf /home/pimp/backups/pimp.tar.gz'
