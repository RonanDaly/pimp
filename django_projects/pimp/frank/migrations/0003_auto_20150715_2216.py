# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0002_auto_20150703_0041'),
    ]

    operations = [
        migrations.RenameField(
            model_name='compound',
            old_name='mass',
            new_name='exact_mass',
        ),
        migrations.RemoveField(
            model_name='compound',
            name='adduct',
        ),
        migrations.RemoveField(
            model_name='compound',
            name='inchiKey',
        ),
        migrations.RemoveField(
            model_name='compound',
            name='ppm',
        ),
        migrations.AddField(
            model_name='compound',
            name='name',
            field=models.CharField(default='something', max_length=500),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='candidateannotation',
            name='analysis',
            field=models.ForeignKey(to='frank.Analysis', null=True),
        ),
    ]
