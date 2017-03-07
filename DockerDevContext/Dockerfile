FROM pimp-base
MAINTAINER Rónán Daly <Ronan.Daly@glasgow.ac.uk>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
        apt-get install -y iputils-ping dnsutils curl gdb && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb
ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

#ENV DEBIAN_FRONTEND noninteractive
# The individual files are being copied here in order to speed up builds
# If no change is made in them, then the cache is okay and can be reused
WORKDIR /home/pimp/pimp/django_projects/pimp
ENV MYSQL_DATABASE=
ENV MYSQL_USER=
ENV MYSQL_PASSWORD=
VOLUME /home/pimp/media /home/pimp/backups /home/pimp/frank
USER pimp
