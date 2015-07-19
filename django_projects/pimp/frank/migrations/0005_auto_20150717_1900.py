# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0004_auto_20150717_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationquery',
            name='status',
            field=models.CharField(default=b'Defined', max_length=250, choices=[(b'Submitted', b'Submitted'), (b'Processing', b'Processing'), (b'Completed', b'Completed')]),
        ),
        migrations.AlterField(
            model_name='fragmentationset',
            name='status',
            field=models.CharField(default=b'Submitted', max_length=250, choices=[(b'Submitted', b'Submitted'), (b'Processing', b'Processing'), (b'Completed', b'Completed')]),
        ),
    ]
