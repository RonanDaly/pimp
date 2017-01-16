FROM pimp-base
MAINTAINER Rónán Daly <Ronan.Daly@glasgow.ac.uk>

#ENV DEBIAN_FRONTEND noninteractive
# The individual files are being copied here in order to speed up builds
# If no change is made in them, then the cache is okay and can be reused
COPY DockerSupport /home/pimp/pimp/DockerSupport
COPY virtualenv /home/pimp/pimp/virtualenv
COPY django_projects/requirements*.txt /home/pimp/pimp/django_projects/
COPY packrat /home/pimp/pimp/packrat
COPY PiMP /home/pimp/pimp/PiMP
COPY PiMPDB /home/pimp/pimp/PiMPDB
COPY setup_docker_prod.sh setup_pimp_prod.sh setupR.R /home/pimp/pimp/
RUN chown -R pimp:pimp /home/pimp
USER pimp
WORKDIR /home/pimp/pimp
RUN ./setup_docker_prod.sh
USER root
COPY . /home/pimp/pimp/
RUN chown -R pimp:pimp /home/pimp
USER pimp
RUN ./install_run_sencha_linux.sh
WORKDIR /home/pimp/pimp/django_projects/pimp
ENV MYSQL_DATABASE=
ENV MYSQL_USER=
ENV MYSQL_PASSWORD=
RUN ./collectstatic.sh
VOLUME /home/pimp/static /home/pimp/pimp /home/pimp/media /home/pimp/backups
CMD ./start_pimp_prod.sh
