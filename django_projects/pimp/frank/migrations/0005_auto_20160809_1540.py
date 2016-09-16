# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0004_auto_20150901_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peak',
            name='preferred_candidate_annotation',
            field=models.ForeignKey(related_name=b'preferred_annotation', on_delete=django.db.models.deletion.SET_NULL, to='frank.CandidateAnnotation', null=True),
        ),
    ]
