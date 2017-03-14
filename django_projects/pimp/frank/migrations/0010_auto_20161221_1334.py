# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0009_auto_20161017_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='compound',
            name='csid',
            field=models.CharField(max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compound',
            name='hmdb_id',
            field=models.CharField(max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='compound',
            name='exact_mass',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=10),
        ),
    ]
