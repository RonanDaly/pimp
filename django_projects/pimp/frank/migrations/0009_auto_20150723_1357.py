# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('frank', '0008_auto_20150719_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotationquery',
            name='massBank_params',
            field=models.CharField(default='something', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='annotationquery',
            name='parent_annotation_query',
            field=models.ForeignKey(to='frank.AnnotationQuery', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='adduct',
            field=models.CharField(default='adduct', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='difference_from_peak_mass',
            field=models.DecimalField(default=1.01, max_digits=20, decimal_places=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='instrument_type',
            field=models.CharField(default='LCMS', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='candidateannotation',
            name='mass_match',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='compound',
            name='inchikey',
            field=models.CharField(max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compoundrepository',
            name='repository_identifier',
            field=models.CharField(default='Something', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='peak',
            name='preferred_candidate_annotation',
            field=models.ForeignKey(to='frank.AnnotationQuery', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peak',
            name='preferred_candidate_description',
            field=models.CharField(max_length=250, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peak',
            name='preferred_candidate_updated_date',
            field=models.DateTimeField(default=django.utils.datetime_safe.date.today, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='peak',
            name='preferred_candidate_user_selector',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='samplefile',
            name='polarity',
            field=models.CharField(max_length=250, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative')]),
        ),
    ]
