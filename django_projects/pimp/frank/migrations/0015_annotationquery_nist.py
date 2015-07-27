# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0014_auto_20150725_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotationquery',
            name='nist',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
