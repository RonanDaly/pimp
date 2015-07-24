# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0011_auto_20150723_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateannotation',
            name='additional_information',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='candidateannotation',
            name='adduct',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='candidateannotation',
            name='collision_energy',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='candidateannotation',
            name='instrument_type',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
