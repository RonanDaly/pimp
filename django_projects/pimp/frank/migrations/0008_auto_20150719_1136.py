# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0007_auto_20150717_2344'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotationquery',
            name='experiment',
        ),
        migrations.AddField(
            model_name='annotationquery',
            name='fragmentation_set',
            field=models.ForeignKey(default=1, to='frank.FragmentationSet'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='annotationquery',
            name='massBank',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
