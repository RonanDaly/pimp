# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import frank.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeCreated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CandidateAnnotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('confidence', models.DecimalField(max_digits=20, decimal_places=10)),
                ('analysis', models.ForeignKey(to='frank.Analysis')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('formula', models.CharField(max_length=250)),
                ('inchiKey', models.CharField(max_length=250)),
                ('ppm', models.DecimalField(max_digits=20, decimal_places=10)),
                ('adduct', models.CharField(max_length=250)),
                ('mass', models.DecimalField(max_digits=20, decimal_places=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompoundRepository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('compound', models.ForeignKey(to='frank.Compound')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('timeCreated', models.DateTimeField(auto_now=True)),
                ('lastModified', models.DateTimeField(auto_now_add=True)),
                ('ionisationMethod', models.CharField(max_length=250, choices=[(b'EIS', b'Electron Ionisation Spray')])),
                ('detectionMethod', models.CharField(max_length=250, choices=[(b'LCMS DDA', b'Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'), (b'GCMS EII', b'Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation'), (b'DIA', b'Data Independent Acquisition')])),
                ('slug', models.SlugField(unique=True)),
                ('createdBy', models.ForeignKey(related_name=b'experiment_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentalCondition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('slug', models.SlugField(unique=True)),
                ('experiment', models.ForeignKey(to='frank.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Peak',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mass', models.DecimalField(max_digits=20, decimal_places=10)),
                ('retentionTime', models.DecimalField(max_digits=20, decimal_places=10)),
                ('intensity', models.DecimalField(max_digits=20, decimal_places=10)),
                ('msnLevel', models.IntegerField(default=0)),
                ('annotations', models.ManyToManyField(to='frank.Compound', through='frank.CandidateAnnotation')),
                ('parentPeak', models.ForeignKey(to='frank.Peak')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('organism', models.CharField(max_length=250)),
                ('slug', models.SlugField(unique=True)),
                ('experimentalCondition', models.ForeignKey(to='frank.ExperimentalCondition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SampleFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('polarity', models.CharField(max_length=250, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative')])),
                ('address', models.FileField(upload_to=frank.models.get_upload_file_name)),
                ('sample', models.ForeignKey(to='frank.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserExperiments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('experiment', models.ForeignKey(to='frank.Experiment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='peak',
            name='sourceFile',
            field=models.ForeignKey(to='frank.SampleFile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='frank.UserExperiments'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compoundrepository',
            name='repository',
            field=models.ForeignKey(to='frank.Repository'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compound',
            name='repository',
            field=models.ManyToManyField(to='frank.Repository', through='frank.CompoundRepository'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='compound',
            field=models.ForeignKey(to='frank.Compound'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='peak',
            field=models.ForeignKey(to='frank.Peak'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='analysis',
            name='experiment',
            field=models.ForeignKey(to='frank.Experiment'),
            preserve_default=True,
        ),
    ]
