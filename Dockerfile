FROM pimp-base
MAINTAINER Rónán Daly <Ronan.Daly@glasgow.ac.uk>

ENV DEBIAN_FRONTEND noninteractive
COPY * /home/pimp
RUN chown -R pimp:pimp /home/pimp
USER pimp
WORKDIR /home/pimp/pimp
RUN setup_docker.sh
WORKDIR /home/pimp/pimp/django_projects/pimp
CMD start_pimp.sh
