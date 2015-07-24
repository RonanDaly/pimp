# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0012_auto_20150724_0057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateannotation',
            name='difference_from_peak_mass',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=10),
        ),
        migrations.AlterField(
            model_name='candidateannotation',
            name='mass_match',
            field=models.NullBooleanField(),
        ),
    ]
