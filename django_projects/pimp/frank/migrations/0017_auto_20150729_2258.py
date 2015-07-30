# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import frank.models


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0016_compound_cas_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='samplefile',
            name='address',
            field=models.FileField(max_length=500, upload_to=frank.models.get_upload_file_name),
        ),
    ]
