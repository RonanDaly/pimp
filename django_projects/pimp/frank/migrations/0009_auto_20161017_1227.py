# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0008_auto_20161011_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='samplefile',
            name='polarity',
            field=models.CharField(max_length=250),
        ),
    ]
