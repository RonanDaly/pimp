FROM pimp
MAINTAINER Rónán Daly <Ronan.Daly@glasgow.ac.uk>

WORKDIR /home/pimp/pimp/django_projects/pimp
RUN ../../venv/bin/honcho -f Procfile.docker export supervisord /etc/supervisor/conf.d/pimp.conf -u pimp --template-dir=../../python_support/honcho
USER pimp
RUN source ../../venv/bin/activate
RUN honcho -f Procfile.docker run python manage.py collectstatic

