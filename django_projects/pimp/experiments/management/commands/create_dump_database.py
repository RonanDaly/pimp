import os
from test.test_support import EnvironmentVarGuard

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection

from experiments.tests import initialise_database, create_database


class Command(BaseCommand):
    help = 'Create a test database from scratch and dump it'

    def handle(self, *args, **options):
        settings.MEDIA_ROOT = settings.TEST_MEDIA_ROOT
        connection.creation.create_test_db(verbosity=2)
        fixture_dir, _, _ = initialise_database()
        env = EnvironmentVarGuard()
        env.set('PIMP_DATABASE_NAME', settings.TEST_DATABASE_NAME)
        env.set('PIMP_MEDIA_ROOT', settings.TEST_MEDIA_ROOT)
        os.mkdir(settings.TEST_MEDIA_ROOT)
        with env:
            create_database(fixture_dir, env)
        dump_path = os.path.join(settings.BASE_DIR, 'fixtures',
                                 'test_database.json')
        with open(dump_path, 'w') as f:
            call_command('dumpdata', indent=4, stdout=f)

        connection.creation.destroy_test_db(settings.TEST_DATABASE_NAME, verbosity=2)
        settings.MEDIA_ROOT = settings.NORMAL_MEDIA_ROOT
