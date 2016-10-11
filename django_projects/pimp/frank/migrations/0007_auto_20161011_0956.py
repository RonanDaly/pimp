# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '__first__'),
        ('frank', '0006_auto_20161010_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='PimpProjectFrankExp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frank_expt', models.ForeignKey(to='frank.Experiment')),
                ('pimp_project', models.ForeignKey(to='projects.Project', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='annotationquery',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='title',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='fragmentationset',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='sample',
            name='name',
            field=models.CharField(max_length=250),
        ),
    ]
