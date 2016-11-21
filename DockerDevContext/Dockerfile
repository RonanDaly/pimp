FROM pimp-base
MAINTAINER Rónán Daly <Ronan.Daly@glasgow.ac.uk>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
        apt-get install -y iputils-ping dnsutils vim curl less

#ENV DEBIAN_FRONTEND noninteractive
# The individual files are being copied here in order to speed up builds
# If no change is made in them, then the cache is okay and can be reused
WORKDIR /home/pimp/pimp/django_projects/pimp
ENV MYSQL_DATABASE=
ENV MYSQL_USER=
ENV MYSQL_PASSWORD=
VOLUME /home/pimp/media /home/pimp/backups
USER pimp
