# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0003_auto_20150715_2216'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('timeCreated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'Defined', max_length=250, choices=[(b'Defined', b'Defined'), (b'Submitted', b'Defined'), (b'Completed', b'Completed')])),
                ('slug', models.SlugField(unique=True)),
                ('experiment', models.ForeignKey(to='frank.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FragmentationSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('timeCreated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'Defined', max_length=250, choices=[(b'Defined', b'Defined'), (b'Submitted', b'Defined'), (b'Completed', b'Completed')])),
                ('slug', models.SlugField(unique=True)),
                ('experiment', models.ForeignKey(to='frank.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='analysis',
            name='experiment',
        ),
        migrations.RemoveField(
            model_name='candidateannotation',
            name='analysis',
        ),
        migrations.DeleteModel(
            name='Analysis',
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='annotation_query',
            field=models.ForeignKey(to='frank.AnnotationQuery', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peak',
            name='fragmentation_set',
            field=models.ForeignKey(default=1, to='frank.FragmentationSet'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='detectionMethod',
            field=models.CharField(max_length=250, choices=[(b'LCMS DDA', b'Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'), (b'LCMS DIA', b'Liquid-Chromatography Data-Independent Acquisition'), (b'GCMS EII', b'Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation')]),
        ),
        migrations.AlterField(
            model_name='samplefile',
            name='polarity',
            field=models.CharField(max_length=250, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative'), (b'Pooled', b'Pooled')]),
        ),
    ]
