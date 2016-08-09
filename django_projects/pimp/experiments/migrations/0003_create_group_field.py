# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_groupings(apps, schema_editor):
    AttributeComparison = apps.get_model('experiments', 'AttributeComparison')
    for ac in AttributeComparison.objects.all():
        if ac.control:
            ac.group = 0
        else:
            ac.group = 1
        ac.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0002_auto_20160721_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributecomparison',
            name='group',
            field=models.IntegerField(null=True),
            preserve_default=False,
        ),
        migrations.RunPython(create_groupings),
        migrations.RemoveField(
            model_name='attributecomparison',
            name='control',
        ),
        migrations.AlterField(
            model_name='attributecomparison',
            name='group',
            field=models.IntegerField(null=False),
        ),
    ]
