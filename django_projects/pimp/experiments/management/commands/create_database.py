from django.core.management.base import BaseCommand

from experiments.tests import initialise_database, create_database


class Command(BaseCommand):
    help = 'Creates a test database from scratch'

    def handle(self, *args, **options):
        fixture_dir, test_media_root, env = initialise_database()
        create_database(fixture_dir, env)
