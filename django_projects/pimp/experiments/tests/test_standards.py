from django.test import TransactionTestCase, override_settings

from experiments.tests.tests import initialise_database, create_database


class StandardCSVTestCase(TransactionTestCase):

    def setup(self):
        pass

    @override_settings(DEBUG=True)
    def test_bad_compound_csv(self):
        test_csv = ('badCompound',)

        fixture_dir, test_media_root, env = initialise_database()
        _, _, _, _ = create_database(fixture_dir, env, test_csv)
