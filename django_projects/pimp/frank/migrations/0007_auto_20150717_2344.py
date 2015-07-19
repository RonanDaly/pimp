# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0006_peak_peak_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='peak',
            old_name='peak_slug',
            new_name='slug',
        ),
    ]
