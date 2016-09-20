# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from experiments.management.commands import populate_parameters

class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
        ('frank', '0004_auto_20150901_1311')
    ]

    operations = [
        migrations.RunPython(populate_parameters.populate),
    ]
