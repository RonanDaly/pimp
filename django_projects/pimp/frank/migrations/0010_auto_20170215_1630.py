# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from projects.views import create_frank_project_objects

def create_missing_frank_objects(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    PimpProjectFrankExp = apps.get_model('frank', 'PimpProjectFrankExp')
    
    for project in Project.objects.all():
        if not PimpProjectFrankExp.objects.filter(pimp_project=project).exists():
            create_frank_project_objects(user=project.user_owner, title=project.title,
                description=project.description, new_project=project) 

class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0009_auto_20161017_1227'),
    ]

    operations = [
        migrations.RunPython(create_missing_frank_objects),
    ]
