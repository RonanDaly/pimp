# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0010_auto_20150723_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateannotation',
            name='additional_information',
            field=models.CharField(default='something', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='collision_energy',
            field=models.CharField(default='10', max_length=500),
            preserve_default=False,
        ),
    ]
