# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0005_auto_20150717_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='peak',
            name='peak_slug',
            field=models.SlugField(default=2, unique=True),
            preserve_default=False,
        ),
    ]
