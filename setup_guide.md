# Setup guide

This is a setup guide for the PiMP pipeline. It contains instructions for Linux (tested on Ubuntu 15.04 & Fedora 21) and Mac OS X Yosemite.

## 0. git Setup

To work with large binary files in the repository install git-lfs

  $ brew install git-lfs

In the repository, run these commands

  $ git config --add lfs.url "http://poisson.tcrc.gla.ac.uk/polyomics/pimp.git/info/lfs"
  $ git lfs install

## 1. System Setup

### Java
Install [Java](https://java.com/en/) version 8, or make sure it is installed (run `java -version` from the command line to check).

**(Linux)** Linux often comes with OpenJDK pre-installed by default but [it's probably better to get Oracle's JDK](http://askubuntu.com/questions/521145/how-to-install-oracle-java-on-ubuntu-14-04).

**(OS X)** Install Java via [Homebrew](http://brew.sh/) (`brew update && brew cask install java`)

### R

Install [R](https://www.r-project.org/) version 3.2, or make sure it is installed (run `R --version` from the command line to check).

**(Linux)** Install R via your package manager

**(OS X)** R can easily be [installed via Homebrew](http://stackoverflow.com/questions/20457290/installing-r-with-homebrew)

### Python

Install [Python](https://www.python.org/) version 2.7, or make sure it is installed (run `python --version` from the command line to check).

**(Linux)** Python should already be installed.

**(OS X)** Python should already be installed.

### RabbitMQ

We need to set up a message queuing server to handle batch jobs. Install [RabbitMQ](https://www.rabbitmq.com) for this. Version 3.5.6 was used for development.

**(Linux)** Install via your package manager or from the website above.

**(OS X)** Install via homebrew (`brew install rabbitmq`)

### Tools and Libraries

Compilation tools and libraries are needed by some of the dependencies in the system.

3. **(OSX)** Install the `XCode` command line tools and various libraries.

        $ xcode-select --install
        $ brew install mysql netcdf gcc48 xquartz openssl
        $ brew link openssl

4. **(Ubuntu)** Install various libraries.

        $ sudo apt-get install libmysqlclient-dev libxml2-dev libxslt1-dev libcurl4-openssl-dev

5. **(Fedora)** Install various libraries.

        $ sudo yum install mysql-devel libxml-devel libxslt-devel cmake qt-devel qt-config
        $ ln -s /usr/bin/qmake-4 /usr/bin/qmake # workaround ..

## 2. Setting up PiMP

1. Go to the `django_projects\pimp` directory and copy one of the example environment files to the `.env` file. The `example-dev.env` file contains an environment you might want to set during development, whilst the `example-prod.env` file contains an environment more suitable for production. E.g.

        $ cp example-dev.env .env

2. Edit the `.env` file for your environment

 **(OSX)** Make sure the DYLD_LIBRARY_PATH variable is set to the library folder
 for your 1.8 JVM. This is to work around a bug with rJava finding the correct
 JVM at runtime.

3. Run the following command in the project root directory

        $ ./gradlew setupPiMP

## 3. Running PiMP

The initial PiMP setup created a virtual environment in `venv` in the project root directory. To enter the virtual environment there is a script you can run.

1. From the project root directory run

        $ . venv/bin/activate

   You will know you are in the virtual environment, because your prompt will change. You can exit the virtual environment by running `deactivate`.

2. Whilst in the virtual environment change to the `django_projects/pimp` directory and run

        $ honcho start

## 4. Setting up Python for development work

1. Install virtualenvwrapper for python. This lets you work in a Python virtual environment -- useful to prevent package conflicts etc.

        $ pip install virtualenvwrapper

2. Add the following lines to your shell startup file (~/.bashrc) to set the location where the virtual environments should live (WORKON_HOME) and the location of your development project directories (PROJECT_HOME). Save the changes to ~/.bashrc.

        export WORKON_HOME=$HOME/.virtualenvs
        export PROJECT_HOME=$HOME/git/pimp
        source /usr/bin/virtualenvwrapper.sh

3. Reload .bashrc and create the directory to hold the virtual environments.

        $ source ~/.bashrc
        $ mkdir -p $WORKON_HOME

## 5. Quick Start Database for FrAnK developers

A sample SQLite database is provided at $PROJECT_HOME/django_projects/test_data/testdb.db. This file contains several fragmentation sets which can be readily annotated by any new annotation tool you've developed. To use this, copy testdb.db to replace the sqlite db you'd created during migrate (in step 5), e.g.

        (venv)$ cp $PROJECT_HOME/django_projects/test_data/testdb.db $PROJECT_HOME/django_projects/pimp/sqlite3.db

Use the user id "testuser" and password "testuser" for login later.
