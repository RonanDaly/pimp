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
            name='AnnotationQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
                ('time_created', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'Defined', max_length=250, choices=[(b'Submitted', b'Submitted'), (b'Processing', b'Processing'), (b'Completed Successfully', b'Completed Successfully'), (b'Completed with Errors', b'Completed with Errors')])),
                ('slug', models.SlugField(unique=True)),
                ('annotation_tool_params', models.CharField(max_length=500, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnnotationQueryHierarchy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_annotation_query', models.ForeignKey(related_name=b'parent_query', to='frank.AnnotationQuery')),
                ('subquery_annotation_query', models.ForeignKey(related_name=b'subquery', to='frank.AnnotationQuery')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnnotationTool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
                ('default_params', models.CharField(max_length=500)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnnotationToolProtocol',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('annotation_tool', models.ForeignKey(to='frank.AnnotationTool')),
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
                ('mass_match', models.NullBooleanField()),
                ('difference_from_peak_mass', models.DecimalField(null=True, max_digits=20, decimal_places=10)),
                ('adduct', models.CharField(max_length=500, null=True)),
                ('instrument_type', models.CharField(max_length=500, null=True)),
                ('collision_energy', models.CharField(max_length=500, null=True)),
                ('additional_information', models.CharField(max_length=500, null=True)),
                ('slug', models.SlugField(unique=True)),
                ('annotation_query', models.ForeignKey(to='frank.AnnotationQuery', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=225)),
                ('formula', models.CharField(max_length=250)),
                ('exact_mass', models.DecimalField(max_digits=20, decimal_places=10)),
                ('inchikey', models.CharField(max_length=500, null=True)),
                ('cas_code', models.CharField(max_length=500, null=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompoundAnnotationTool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('annotation_tool_identifier', models.CharField(max_length=500)),
                ('annotation_tool', models.ForeignKey(to='frank.AnnotationTool')),
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
                ('title', models.CharField(unique=True, max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('time_created', models.DateTimeField(auto_now=True)),
                ('ionisation_method', models.CharField(max_length=250, choices=[(b'EIS', b'Electron Ionisation Spray'), (b'EII', b'Electron Impact Ionisation')])),
                ('slug', models.SlugField(unique=True)),
                ('created_by', models.ForeignKey(related_name=b'experiment_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentalCondition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('slug', models.SlugField(unique=True)),
                ('experiment', models.ForeignKey(to='frank.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentalProtocol',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FragmentationSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
                ('time_created', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'Submitted', max_length=250, choices=[(b'Submitted', b'Submitted'), (b'Processing', b'Processing'), (b'Completed Successfully', b'Completed Successfully'), (b'Completed with Errors', b'Completed with Errors')])),
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
                ('retention_time', models.DecimalField(max_digits=20, decimal_places=10)),
                ('intensity', models.DecimalField(max_digits=30, decimal_places=10)),
                ('msn_level', models.IntegerField()),
                ('slug', models.SlugField(unique=True)),
                ('preferred_candidate_description', models.CharField(max_length=500, null=True)),
                ('preferred_candidate_updated_date', models.DateTimeField(null=True)),
                ('annotations', models.ManyToManyField(to='frank.Compound', through='frank.CandidateAnnotation')),
                ('fragmentation_set', models.ForeignKey(to='frank.FragmentationSet')),
                ('parent_peak', models.ForeignKey(to='frank.Peak', null=True)),
                ('preferred_candidate_annotation', models.ForeignKey(related_name=b'preferred_annotation', to='frank.CandidateAnnotation', null=True)),
                ('preferred_candidate_user_selector', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('organism', models.CharField(max_length=250)),
                ('slug', models.SlugField(unique=True)),
                ('experimental_condition', models.ForeignKey(to='frank.ExperimentalCondition')),
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
                ('address', models.FileField(max_length=500, upload_to=frank.models._get_upload_file_name)),
                ('sample', models.ForeignKey(to='frank.Sample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserExperiment',
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
            name='source_file',
            field=models.ForeignKey(to='frank.SampleFile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='detection_method',
            field=models.ForeignKey(to='frank.ExperimentalProtocol'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='frank.UserExperiment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compound',
            name='annotation_tool',
            field=models.ManyToManyField(to='frank.AnnotationTool', through='frank.CompoundAnnotationTool'),
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
            model_name='annotationtoolprotocol',
            name='experimental_protocol',
            field=models.ForeignKey(to='frank.ExperimentalProtocol'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='annotationtool',
            name='suitable_experimental_protocols',
            field=models.ManyToManyField(to='frank.ExperimentalProtocol', through='frank.AnnotationToolProtocol'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='annotationquery',
            name='annotation_tool',
            field=models.ForeignKey(to='frank.AnnotationTool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='annotationquery',
            name='fragmentation_set',
            field=models.ForeignKey(to='frank.FragmentationSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='annotationquery',
            name='source_annotation_queries',
            field=models.ManyToManyField(to='frank.AnnotationQuery', through='frank.AnnotationQueryHierarchy'),
            preserve_default=True,
        ),
    ]
