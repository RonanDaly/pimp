FROM pimp-base
MAINTAINER Rónán Daly <Ronan.Daly@glasgow.ac.uk>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
        apt-get install -y iputils-ping dnsutils vim curl less git
# The pimp source needs to be available at /home/pimp/pimp by this point
USER pimp
WORKDIR /home/pimp/pimp/django_projects/pimp
RUN collectstatic.sh
