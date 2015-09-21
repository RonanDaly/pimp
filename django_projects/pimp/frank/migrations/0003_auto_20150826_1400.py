# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0002_auto_20150822_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='ionisation_method',
            field=models.CharField(max_length=250, choices=[(b'ESI', b'Electrospray Ionisation'), (b'EII', b'Electron Impact Ionisation')]),
        ),
    ]
