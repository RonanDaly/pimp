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
		cmake \
		#libatlas3-base \
		#libatlas-dev \
		oracle-java8-installer \
		r-base \
		rabbitmq-server && \
	apt-get install -y oracle-java8-set-default
		

RUN groupadd pimp && useradd -g pimp -m pimp
#ADD pwiz-bin-windows-x86-vc100-release-3_0_5655.tar.bz2 /home/ransom/
COPY winetricks /home/pimp/
WORKDIR /home/pimp
RUN chown -R pimp:pimp winetricks
USER pimp
ENV WINEARCH win32
ENV WINEPREFIX /home/pimp/.wine

# We need to sleep, because wine launches a background process to do its
# tasks, finishing whenever it want to. 10 seconds _should_ be enough
RUN wine cmd.exe /c echo %ProgramFiles% && sleep 10
RUN xvfb-run ./winetricks -q winxp vcrun2005 vcrun2008 dotnet20 dotnet40 && sleep 10 && rm -rf ~/.cache ~/.local ~/.config

#RUN apt-get purge -y xvfb &&
#	apt-get clean autoclean &&
#	apt-get autoremove -y &&
#	rm -rf /var/lib/{apt,dpkg,cache,log}/ &&
#	rm -rf ~/.cache ~/.local ~/.config

# Known good version pwiz-bin-windows-x86-vc90-release-2_2_3309.tar.bz2
# Known good version Pwiz_3_0_5655

# Known bad version  pwiz-bin-windows-x86-vc120-release-3_0_7506.tar.bz2
