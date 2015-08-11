# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peak',
            name='intensity',
            field=models.DecimalField(max_digits=30, decimal_places=10),
        ),
    ]
