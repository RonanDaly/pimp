# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '__first__'),
        ('experiments', '0002_auto_20160721_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('analysis', models.ForeignKey(to='experiments.Analysis')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Peak',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('secondaryId', models.IntegerField(db_index=True, null=True, blank=True)),
                ('mass', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('rt', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('polarity', models.CharField(max_length=8, null=True, blank=True)),
                ('type', models.CharField(max_length=100, null=True, blank=True)),
                ('dataset', models.ForeignKey(to='data.Dataset')),
            ],
            options={
                'ordering': ['secondaryId'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeakDtComparison',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logFC', models.FloatField(null=True, blank=True)),
                ('pValue', models.FloatField(null=True, blank=True)),
                ('adjPvalue', models.FloatField(null=True, blank=True)),
                ('logOdds', models.FloatField(null=True, blank=True)),
                ('comparison', models.ForeignKey(to='experiments.Comparison')),
                ('peak', models.ForeignKey(to='data.Peak')),
            ],
            options={
                'ordering': ['comparison'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeakDTSample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intensity', models.FloatField(null=True, blank=True)),
                ('peak', models.ForeignKey(to='data.Peak')),
                ('sample', models.ForeignKey(to='fileupload.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeakQCSample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intensity', models.FloatField(null=True, blank=True)),
                ('peak', models.ForeignKey(to='data.Peak')),
                ('sample', models.ForeignKey(to='fileupload.CalibrationSample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
