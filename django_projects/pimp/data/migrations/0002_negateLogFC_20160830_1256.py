# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def negate_log_fc(apps, schema_editor):
    PeakDtComparison = apps.get_model('data', 'PeakDtComparison')
    for pdtc in PeakDtComparison.objects.all():
        pdtc.logFC = -pdtc.logFC
        pdtc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(negate_log_fc),
    ]
