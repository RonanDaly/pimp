# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='peakdtcomparison',
            name='comparison',
            field=models.ForeignKey(to='experiments.Comparison'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peakdtcomparison',
            name='peak',
            field=models.ForeignKey(to='data.Peak'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peak',
            name='dataset',
            field=models.ForeignKey(to='data.Dataset'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataset',
            name='analysis',
            field=models.ForeignKey(to='experiments.Analysis'),
            preserve_default=True,
        ),
    ]
