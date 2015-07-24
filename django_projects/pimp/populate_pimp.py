import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings_dev')

import django
django.setup()

from experiments.models import DefaultParameter, Database
from frank.models import Repository

def populate():
    iqr_parameter = add_default_parameter(
        name = "iqr",
        value = 0.5,
        state = True,
    )

    rsd_parameter = add_default_parameter(
        name = "rsd",
        value = 0.5,
        state = True,
    )

    noise_parameter = add_default_parameter(
        name = "noise",
        value = 0.8,
        state = True,
    )

    ppm_parameter = add_default_parameter(
        name = "ppm",
        value = 3,
        state = True,
    )

    min_detection = add_default_parameter(
        name = "mindetection",
        value = 3,
        state = True,
    )

    min_intensity = add_default_parameter(
        name = "minintensity",
        value = 5000,
        state = True,
    )

    rt_window = add_default_parameter(
        name = "rtwindow",
        value = 0.05,
        state = True,
    )

    rt_alignment = add_default_parameter(
        name = "rt.alignment",
        value = None,
        state = True,
    )

    normalization = add_default_parameter(
        name = "normalization",
        value = None,
        state = False,
    )

    kegg_db = add_database(
        name = "kegg"
    )

    kegg_db = add_database(
        name = "hmdb"
    )

    kegg_db = add_database(
        name = "lipidmaps"
    )

    mass_bank_repository = add_repository(
        name = 'MassBank'
    )



def add_default_parameter(name, value, state):
    parameter = DefaultParameter.objects.get_or_create(
        name = name,
        value = value,
        state = state,
    )[0]
    print 'Creating default parameter - '+name+'...'
    parameter.save()
    return parameter

def add_database(name):
    database = Database.objects.get_or_create(
       name = name,
    )[0]
    print 'Creating default database - '+name+'...'
    database.save()
    return database

def add_repository(name):
    repository = Repository.objects.get_or_create(
       name = name,
    )[0]
    print 'Creating default repository - '+name+'...'
    repository.save()
    return repository

# Execution starts here
if __name__=='__main__':
    print "Populating default parameters..."
    populate()