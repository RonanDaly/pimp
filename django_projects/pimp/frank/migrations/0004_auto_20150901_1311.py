# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0003_auto_20150826_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compound',
            name='name',
            field=models.CharField(max_length=250),
        ),
    ]
