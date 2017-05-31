# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0011_auto_20161221_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='ionisation_method',
            field=models.CharField(max_length=250, choices=[(b'ESI', b'Electrospray Ionisation')]),
        ),
    ]
