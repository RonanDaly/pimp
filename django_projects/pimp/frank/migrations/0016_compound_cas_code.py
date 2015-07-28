# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0015_annotationquery_nist'),
    ]

    operations = [
        migrations.AddField(
            model_name='compound',
            name='cas_code',
            field=models.CharField(max_length=500, null=True),
            preserve_default=True,
        ),
    ]
