# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('frank', '0017_auto_20150729_2258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peak',
            name='preferred_candidate_annotation',
        ),
        migrations.RemoveField(
            model_name='peak',
            name='preferred_candidate_description',
        ),
        migrations.RemoveField(
            model_name='peak',
            name='preferred_candidate_updated_date',
        ),
        migrations.RemoveField(
            model_name='peak',
            name='preferred_candidate_user_selector',
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='preferred_candidate_annotation',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='preferred_candidate_description',
            field=models.CharField(max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='preferred_candidate_updated_date',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='preferred_candidate_user_selector',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
