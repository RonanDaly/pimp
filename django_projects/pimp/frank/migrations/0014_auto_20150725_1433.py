# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frank', '0013_auto_20150724_1316'),
    ]

    operations = [
        migrations.RenameField(
            model_name='annotationquery',
            old_name='timeCreated',
            new_name='time_created',
        ),
        migrations.RenameField(
            model_name='experiment',
            old_name='createdBy',
            new_name='created_by',
        ),
        migrations.RenameField(
            model_name='experiment',
            old_name='detectionMethod',
            new_name='detection_method',
        ),
        migrations.RenameField(
            model_name='experiment',
            old_name='ionisationMethod',
            new_name='ionisation_method',
        ),
        migrations.RenameField(
            model_name='experiment',
            old_name='lastModified',
            new_name='last_modified',
        ),
        migrations.RenameField(
            model_name='experiment',
            old_name='timeCreated',
            new_name='time_created',
        ),
        migrations.RenameField(
            model_name='fragmentationset',
            old_name='timeCreated',
            new_name='time_created',
        ),
        migrations.RenameField(
            model_name='peak',
            old_name='msnLevel',
            new_name='msn_level',
        ),
        migrations.RenameField(
            model_name='peak',
            old_name='parentPeak',
            new_name='parent_peak',
        ),
        migrations.RenameField(
            model_name='peak',
            old_name='retentionTime',
            new_name='retention_time',
        ),
        migrations.RenameField(
            model_name='peak',
            old_name='sourceFile',
            new_name='source_file',
        ),
        migrations.RenameField(
            model_name='sample',
            old_name='experimentalCondition',
            new_name='experimental_condition',
        ),
        migrations.AlterField(
            model_name='annotationquery',
            name='status',
            field=models.CharField(default=b'Defined', max_length=250, choices=[(b'Submitted', b'Submitted'), (b'Processing', b'Processing'), (b'Completed Successfully', b'Completed Successfully'), (b'Completed with Errors', b'Completed with Errors')]),
        ),
        migrations.AlterField(
            model_name='fragmentationset',
            name='status',
            field=models.CharField(default=b'Submitted', max_length=250, choices=[(b'Submitted', b'Submitted'), (b'Processing', b'Processing'), (b'Completed Successfully', b'Completed Successfully'), (b'Completed with Errors', b'Completed with Errors')]),
        ),
    ]
