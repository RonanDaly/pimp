# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import shutil

from django.conf import settings
from django.db import migrations


def move_analysis_xml(apps, schema_editor):

    # for all projects
    Project = apps.get_model('projects', 'Project')
    for p in Project.objects.all():
        project_dir = os.path.join(settings.MEDIA_ROOT, 'projects', str(p.id))
        dir_content = os.listdir(project_dir)

        # find all xml files inside the project folder
        for item in dir_content:
            if item.startswith('analysis') and item.endswith('.xml'):
                filename, file_extension = os.path.splitext(item)
                xml_path = os.path.join(project_dir, item)
                target_path = os.path.join(project_dir, filename, item)
                print 'Found', xml_path, ', moved to', target_path
                shutil.move(xml_path, target_path)

class Migration(migrations.Migration):


    dependencies = [
        ('experiments', '0003_create_group_field'),
    ]

    operations = [
        migrations.RunPython(move_analysis_xml),
    ]
