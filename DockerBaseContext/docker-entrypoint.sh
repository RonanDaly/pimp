#!/bin/bash
set -e

if [ "$(id -u)" = '0' ]; then
	DOCKER_SOCKET_GROUP_ID=$(gosu pimp stat -c %g /var/run/docker.sock)
    DOCKER_SOCKET_GROUP_NAME=$(getent group ${DOCKER_SOCKET_GROUP_ID} | cut -d ':' -f 1)

    if [ -z ${DOCKER_SOCKET_GROUP_NAME+x} ]; then
        groupadd -g ${DOCKER_SOCKET_GROUP_ID} dockersocketgroup
        usermod -aG dockersocketgroup pimp
    else
        usermod -aG ${DOCKER_SOCKET_GROUP_NAME} pimp
    fi

    BIND_GROUP_ID=$(gosu pimp stat -c %g /home/pimp/media)
    BIND_GROUP_NAME=$(getent group ${BIND_GROUP_ID} | cut -d ':' -f 1)

    if [ -z ${BIND_GROUP_NAME+x} ]; then
        groupadd -g ${BIND_GROUP_ID} bindgroup
        usermod -aG bindgroup pimp
    else
        usermod -aG ${BIND_GROUP_NAME} pimp
    fi

	exec gosu pimp "$@"
fi

exec "$@"






