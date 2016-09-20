# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('groups', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('submited', models.DateTimeField(null=True, blank=True)),
                ('owner', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttributeComparison',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('control', models.BooleanField(default=False)),
                ('attribute', models.ForeignKey(to='groups.Attribute')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comparison',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('attribute', models.ManyToManyField(to='groups.Attribute', through='experiments.AttributeComparison')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('state', models.NullBooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-modified'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.DecimalField(null=True, max_digits=20, decimal_places=10, blank=True)),
                ('state', models.NullBooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Params',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('databases', models.ManyToManyField(to='experiments.Database')),
                ('param', models.ManyToManyField(to='experiments.Parameter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comparison',
            name='experiment',
            field=models.ForeignKey(to='experiments.Experiment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attributecomparison',
            name='comparison',
            field=models.ForeignKey(to='experiments.Comparison'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='analysis',
            name='experiment',
            field=models.ForeignKey(to='experiments.Experiment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='analysis',
            name='params',
            field=models.ForeignKey(to='experiments.Params'),
            preserve_default=True,
        ),
    ]
