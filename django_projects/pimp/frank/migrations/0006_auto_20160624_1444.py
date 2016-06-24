# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0005_auto_20160314_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationquery',
            name='annotation_tool_params',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
