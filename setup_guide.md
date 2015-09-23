# Setup guide

This is a setup guide for the PiMP pipeline. It contains instructions for Linux (tested on Ubuntu 15.04 & Fedora 21) and Mac OS X Yosemite. 

## 1. General Setup

1. Install [Java](https://java.com/en/). Linux comes with OpenJDK pre-installed by default but [it's probably better to get Oracle's JDK](http://askubuntu.com/questions/521145/how-to-install-oracle-java-on-ubuntu-14-04).

2. Install [R](https://www.r-project.org/).

3. **(OSX)** Install the `XCode` command line tools.
        $ xcode-select --install

4. **(Ubuntu)** Install various libraries.

        $ sudo apt-get install libmysqlclient-dev libxml2-dev libxslt1-dev libcurl4-openssl-dev

5. **(Fedora)** Install various libraries.

        $ sudo yum install mysql-devel libxml-devel libxslt-devel cmake qt-devel qt-config
        $ ln -s /usr/bin/qmake-4 /usr/bin/qmake # workaround ..

## 2a. Default Python Setup

1. **(OSX)** Install [Homebrew](http://brew.sh/) and use it to install Python
        $ brew install python

2. Install virtualenvwrapper for python. This lets you work in a Python virtual environment -- useful to prevent package conflicts etc. 

        $ sudo pip install virtualenvwrapper

3. Add the following lines to your shell startup file (~/.bashrc) to set the location where the virtual environments should live (WORKON_HOME) and the location of your development project directories (PROJECT_HOME). Save the changes to ~/.bashrc.

        export WORKON_HOME=$HOME/.virtualenvs
        export PROJECT_HOME=$HOME/git/pimp
        source /usr/bin/virtualenvwrapper.sh

4. Reload .bashrc and create the directory to hold the virtual environments.
    
        $ source ~/.bashrc
        $ mkdir -p $WORKON_HOME

5. Then create a virtual environment (here called `venv`), change directory to `$pimp_directory` and install the required Python packages for PiMP and FrAnK.

        $ mkvirtualenv venv
        (venv)$ export pimp_directory=/home/joewandy/git/pimp/ # or wherever appropriate
        (venv)$ pip install -r $pimp_directory/django_projects/requirements.txt
        (venv)$ pip install -r $pimp_directory/django_projects/requirements_frank.txt

## 2b. Anaconda Python setup

[Anaconda Python](https://store.continuum.io/cshop/anaconda/) is a 'completely free enterprise-ready Python distribution for large-scale data processing, predictive analytics, and scientific computing'. It comes preconfigured with many packages which can often be [very tedious]((http://www.continuum.io/blog/conda) to install due to non-Python dependencies (e.g. HDF5, MKL, LLVM). You can use this in place of the default Python interpreter in (2a).

TODO

## 3. R setup

1. Install the R packages required for PiMP and PiMPDB
        $ R
        > install.packages('rJava')
        > install.packages('XML')
        > install.packages('snow')
        > install.packages('caTools')
        > install.packages('bitops')
        > install.packages('ptw')
        > install.packages('gplots')
        > install.packages('tcltk2')
        > install.packages('doParallel')
        > install.packages('gptk')
        > install.packages('outliers')
        > install.packages('XLConnect')
        > install.packages('RJSONIO')
        > install.packages('RCurl')
        > install.packages('R.utils')
        > install.packages('digest')
        > install.packages('RColorBrewer')
        > install.packages('RUnit')
        > install.packages('DBI')

2. In R, install [Bioconductor](https://www.bioconductor.org/install/) and use it to install more Bioconductor packages.

        > source('http://bioconductor.org/biocLite.R')
        > biocLite('xcms')
        > biocLite('multtest')
        > biocLite('mzR')
        > biocLite('impute')
        > biocLite('limma')

4. In R, install [mzMatch](http://mzmatch.sourceforge.net/installation.php) and initialises it to download its database files.

        > source ("http://puma.ibls.gla.ac.uk/mzmatch.R/install_mzmatch.R")
        > require (mzmatch.R)
        > mzmatch.init ()
        > quit()

5. Install the PiMP and PiMPDB packages locally. Needs root permission to place mzmatch_2.0.jar in /usr/local.
        (venv)$ cd $pimp_directory 
        (venv)$ sudo R CMD INSTALL PiMP 
        (venv)$ R CMD INSTALL PiMPDB 

## 4. Message Queuing Setup

We need to set up a message queuing server to handle batch jobs. 

1. Install RabbitMQ following the instruction from https://www.rabbitmq.com

2. Run RabbitMQ server in the background:

        (venv)$ sudo rabbitmq-server start -detached
        
   To stop RabbitMQ, do the following:
   
        (venv)$ sudo -u rabbitmq rabbitmqctl stop

## 5. Run PiMP and Celery

Run the following commands with the virtualenv still active

1. Synchronise the database:

        (venv)$ cd $pimp_directory/django_projects/pimp
        (venv)$ python manage.py migrate --settings=pimp.settings_dev

2. Create a superuser manually then start the server again:

        (venv)$ python manage.py createsuperuser --settings=pimp.settings_dev
        (venv)$ python manage.py runserver --settings=pimp.settings_dev

	and go to `localhost:8000/admin` to add the first and last name of the superuser.

3. Setup the default configuration parameters by using the Django shell:
        (venv)$ python populate_pimp.py

4. Create the temporary directory for django:
        (venv)$ sudo mkdir -p /opt/django/django-cache
	
4. Finally, restart PiMP and also Celery at the same time:
        (venv)$ python manage.py runserver --settings=pimp.settings_dev
        (venv)$ python manage.py celery worker --settings=pimp.settings_dev
