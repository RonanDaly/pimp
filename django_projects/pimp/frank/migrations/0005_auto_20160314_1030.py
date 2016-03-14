# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '__first__'),
        ('data', '__first__'),
        ('frank', '0004_auto_20150901_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='PimpAnalysisFrankFs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=500)),
                ('frank_fs', models.ForeignKey(to='frank.FragmentationSet')),
                ('pimp_analysis', models.ForeignKey(to='experiments.Analysis', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PimpFrankPeakLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frank_peak', models.ForeignKey(to='frank.Peak')),
                ('pimp_peak', models.ForeignKey(to='data.Peak', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='peak',
            name='preferred_candidate_annotation',
            field=models.ForeignKey(related_name=b'preferred_annotation', on_delete=django.db.models.deletion.SET_NULL, to='frank.CandidateAnnotation', null=True),
        ),
    ]
