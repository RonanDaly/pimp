# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0005_auto_20160915_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experimentalcondition',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='experimentalcondition',
            name='slug',
            field=models.SlugField(default=b''),
        ),
    ]
