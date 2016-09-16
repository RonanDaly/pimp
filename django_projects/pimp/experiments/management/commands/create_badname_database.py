from django.core.management.base import BaseCommand

from experiments.tests.tests import initialise_database, create_database


class Command(BaseCommand):
    help = 'Creates a test database from scratch'

    def handle(self, *args, **options):
        test_csv = ('badCompound',)

        fixture_dir, test_media_root, env = initialise_database()
        create_database(fixture_dir, env, test_csv)
