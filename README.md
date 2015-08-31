![alt text](django_projects/static/img/PiMP_logo.png) Welcome to PiMP!
===================

PiMP is an integrated, web-enabled tool for LC-MS data analysis and visualization.
PiMP is built using a python MVC web framework called Django, and the backend pipeline has been developed in R. 

If you just joined the development team and are about to get started, take a few minutes  to read this so you don't get lost in the code. 

----------

Getting started with PiMP and GitLab
-------------

#### Collaborative development
PiMP follows a regulated collaborative development method, which means not everyone can the join but many research groups or individuals participate to its development. It is really likely that you will have to collaborate with other developers in the future, and other developers may also need your help at some point, so for this reason we ask every developer to set their email address as public. Please go to [your profile page](http://newtcrc-panda.ibls.gla.ac.uk/profile) and make sure this is all set.

#### SSH key
You won't be able to pull or push project code via SSH until you [add an SSH key](http://newtcrc-panda.ibls.gla.ac.uk/profile/keys/new) to your profile. You need help setting up your key? Take a look at [this tutorial](http://newtcrc-panda.ibls.gla.ac.uk/help/ssh/README). 


Installation
-------------

#### <i class="icon-cog"></i> Python & Django Installation

Django is a high-level Python MVC Web framework that encourages rapid development and clean, pragmatic design. 

PiMP currently uses python 2.7 and Django 1.7, to install python and Django please follow [these instructions](https://docs.djangoproject.com/en/1.7/intro/install/).

Before you go further, please make sure you are familiar with Django documentation which is accessible [here](https://docs.djangoproject.com/en/1.7/). 

> **Note: Django specific MVC naming system**

> -  Django provides an abstraction layer (the “models”) for structuring and manipulating the data of the Web application (commonly called [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping)). For more details please see [Django Model documentation](https://docs.djangoproject.com/en/1.7/#the-model-layer).
> - Django has the concept of “views” to encapsulate the logic responsible for processing a user’s request and for returning the response.  The "views" in Django correspond to what is called "controller" in a standard MVC framework. Details can be found [here](https://docs.djangoproject.com/en/1.7/#the-view-layer).
> - In Django, the "views" of a standard MVC framework are called templates, you are confused? take a look at [this](https://docs.djangoproject.com/en/1.7/#the-template-layer)...