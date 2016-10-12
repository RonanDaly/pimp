# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0007_auto_20161011_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationtool',
            name='slug',
            field=models.SlugField(default=b''),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='slug',
            field=models.SlugField(default=b''),
        ),
        migrations.AlterField(
            model_name='fragmentationset',
            name='slug',
            field=models.SlugField(default=b''),
        ),
        migrations.AlterField(
            model_name='sample',
            name='slug',
            field=models.SlugField(default=b''),
        ),
    ]
