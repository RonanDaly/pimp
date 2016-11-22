FROM ubuntu:16.04
MAINTAINER Rónán Daly <Ronan.Daly@glasgow.ac.uk>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
	apt-get install -y \
		apt-utils && \
        apt-get install -y \
		software-properties-common && \
	add-apt-repository -y ppa:webupd8team/java && \
        apt-get update && \
	echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
	apt-get install -y \
		libmysqlclient-dev \
		libxml2-dev \
		libxslt1-dev \
		libcurl4-openssl-dev \
		libssl-dev \
		libnetcdf-dev \
		libfreetype6-dev \
		libatlas-base-dev \
		libpython-dev \
        libreadline-dev \
		#Needed for nloptr in R; problem with self downloading
		libnlopt-dev \
        pkg-config \
		#cmake \ # Needed for PySide
		#libatlas3-base \
		#libatlas-dev \
        # Needed for javareconf
        build-essential \
        python-minimal \
        mysql-client-5.7 \
		oracle-java8-installer \
		rabbitmq-server && \
		#supervisor && \
	apt-get install -y oracle-java8-set-default && \
	apt-get install -y r-base && \
    rm -rf /var/lib/apt/lists/* && \
	R CMD javareconf

RUN groupadd pimp && useradd -g pimp -m pimp
RUN mkdir /home/pimp/static /home/pimp/media /home/pimp/backups
RUN chown -R pimp:pimp /home/pimp
