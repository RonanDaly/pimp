# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def remove_gcms_protocols(apps, schema_editor):

    # for all projects
    ExperimentalProtocol = apps.get_model('frank', 'ExperimentalProtocol')
    if ExperimentalProtocol.objects.filter(
            name='Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition').exists():
        lcms_protocol = ExperimentalProtocol.objects.get(
            name='Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'
        )
        lcms_protocol.name = 'Liquid-Chromatography Mass-Spectroscopy'
        lcms_protocol.save()
    if ExperimentalProtocol.objects.filter(
            name='Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation').exists():
        gcms_protocol = ExperimentalProtocol.objects.get(
            name='Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation',
        )
        gcms_protocol.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0004_move_analysis_xml'),
    ]

    operations = [
        migrations.RunPython(remove_gcms_protocols),
    ]
