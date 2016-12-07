Developing PiMP as a Docker container
=====================================

It is possible to run the entire PiMP stack as a Docker container and the
files necessary to build and run the containers are included in the
source code.

Setup
-----
Install [Docker](https://www.docker.com/products/overview) and
[Docker Compose](https://docs.docker.com/compose/). Note that Docker on Mac
and Windows machines come in two flavours: Docker for Mac/Windows and Docker
Toolbox. In this guide we are assuming Docker for Mac/Windows. In particular,
it means that the instructions on the Docker Compose page are outdated, so
Docker Compose will need to be installed separately.

Building the PiMP stack
-----------------------
There are two ways to build the necessary containers. The first is for
development purposes and mounts the current files in the source tree; the
second is for releases and copies the files in, so that the container is
self contained.

### Building the base image ###
Before building the main stacks, the base image needs to be created. Change
to the DockerBaseContext directory and run:

    $ docker-compose build

This will build the pimp-base image that is used later.

### Building and running the Development stack ###
Change to the DockerDevContext and run:

    $ docker-compose build
    $ docker-compose run pimp bash

This will run a bash shell inside the container. From here:

    $ cd /home/pimp/pimp
    $ ./setup_docker_dev.sh

This will create the correct honcho .env and Procfiles and download
and install the correct R and Python dependencies, which will take a while.
When this is done:

    $ cd django_projects/pimp
    $ honcho run python manage.py migrate
    $ honcho run python setupInitialUser.py

you can exit the shell to get back to your own machine.
Then, run:

    $ docker-compose up

This will build, create, start and attach the necessary containers and open
up port 8000 (by default) for connections. You should now have a running
PiMP system.

### Building and running the Release stack ###
Change to the root directory and run:

    $ docker-compose up

This will create, start and attach the necessary containers and open
up port 8080 (by default) for connections. You should now have a running
PiMP system.

PiMP in Docker details
----------------------
There is a fairly complex setup: the complete PiMP stack runs in two containers
in development and three containers in release. The basis for these is the
container defined in ```DockerBaseContext/Dockerfile```. This defines an
Ubuntu 16.04 system with the necessary system dependencies and creates a
user ```pimp``` and directory structure. In all instances, the PiMP django
container runs as user ```pimp```. The ```docker-compose.yml``` file in the
same directory is simply used to ensure the Docker image is
called ```pimp-base```

### Development Stack ###
The development stack is defined in the ```DockerDevContext``` directory.
The ```Dockerfile``` here is quite simple and installs a few utilities and sets
up the correct working directory and user. Most of the configuration is done
in the Docker Compose files. There are three of them ```docker-compose.yml```
,```docker-compose.override.yml``` and ```common.yml```. Note
that ```docker-compose.yml``` and ```common.yml``` are actually symlinks to the
files up one level, which are used for the release build. ```docker-compose```
has been created so that it automatically merges the ```docker-compose.yml```
and ```docker-compose.override.yml``` files by default. Together, the files
define two services, a MySQL service and the PiMP django service.

### Release Stack ###
The release stack is defined in the root directory. The ```Dockerfile``` here
is slightly complicated; the reason for the multiple copies is to try
and limit R and Python rebuilds when a single file changes. When building,
the setup commands will also be run, ensuring a usable image after the build
is finished.

### MySQL service ###
The MySQL service is defined so that it will automatically create a database
if none exists. Environment variables used are ```MYSQL_ALLOW_EMPTY_PASSWORD```
, ```MYSQL_DATABASE```, ```MYSQL_USER```, ```MYSQL_PASSWORD```, which are
defined in the ```.env``` file.

### PiMP service ###
In release mode, The PiMP service is defined so that it will automatically
setup the database if none exists. It will also create an admin user from
the ```PIMP_INITIAL``` variables in the ```.env``` file. In development mode,
the ```start_pimp_dev.sh``` script is run, which waits for the MySQL service
and then runs the django devserver. In release mode,
the ```start_pimp_prod.sh``` script is run, which automatically updates the
database and runs the wsgi webserver.

### Nginx ###
The Nginx service is a custom extension of the standard Docker version,
hardcoded to the PiMP setup. It is only used on the release version.
