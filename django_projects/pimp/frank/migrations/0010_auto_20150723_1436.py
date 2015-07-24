# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0009_auto_20150723_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationquery',
            name='massBank_params',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
