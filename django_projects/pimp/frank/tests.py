from django.test import TestCase
from frank.models import *
from frank.forms import *
from frank.admin import *
from frank.views import *
from peakFactories import *
from annotationTools import *
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils import unittest
from django.test.client import Client
from pimp.settings_dev import BASE_DIR, MEDIA_ROOT
import os
from django.core.files import File
import populate_pimp as population_script


#################### VIEWS TESTS ###################

class IndexTestView(TestCase):
    """
    These are tests for the index view of Frank, we want to test that the
    page renders and that the user who is not authenticated will be redirected
    to the login page (i.e. a test of the @login_required decorator
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )


    def test_index_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        response = self.client.get(reverse('frank_index'))
        self.assertEqual(response.status_code, 200)



    def test_index_with_non_authenticated_client(self):
        response = self.client.get(reverse('frank_index'))
        self.assertRedirects(response, 'accounts/login/?next=/frank/')


class MyExperimentsViewTest(TestCase):
    """
    Test for the my_experiments view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )

    def test_my_experiment_view_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        response = self.client.get(reverse('my_experiments'))
        self.assertEqual(response.status_code, 200)


class AddExperimentViewTest(TestCase):
    """
    Test for the add_experiment view in frank.views. Here we want to test that
    the page renders for an authenticated user. In additon, we want to test that
    the addition submission of a valid form creates and experiment object. Finally,
    we want to ensure that experiment titles cannot be duplicated as this will
    compromise the unique constraint on the experiment slug.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        experiment_2 = Experiment.objects.create(
            title = 'Experiment 2',
            description = 'This is another experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )

    def test_add_experiment_view_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        response = self.client.get(reverse('add_experiment'))
        self.assertEqual(response.status_code, 200)


    def test_addition_of_new_experiment(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/my_experiments.html'):
            response = self.client.post(reverse(
                'add_experiment'),
                {'title': 'Experiment 1',
                'description': 'This is a test experiment',
                'ionisation_method': 'EIS',
                'detection_method': '1'
                }
            )
        self.assertEqual(response.status_code, 200)
        experiment = Experiment.objects.get(title = 'Experiment 1')
        self.assertTrue(isinstance(experiment, Experiment))


    def test_to_ensure_duplicate_experiment_titles_constraint_holds(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/add_experiment.html'):
            response = self.client.post(reverse(
                'add_experiment'),
                {'title': 'Experiment 2',
                'description': 'This is a test experiment',
                'ionisation_method': 'EIS',
                'detection_method': '1'
                }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'experiment_form', 'title', 'Experiment with this Title already exists.')


class ExperimentSummaryViewTest(TestCase):
    """
    Test for the add_experiment view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )


    def test_experiment_summary_page_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/experiment.html'):
            self.client.get(reverse('experiment_summary', kwargs={'experiment_name_slug': self.experiment.slug}))


class AddExperimentalConditionViewTest(TestCase):
    """
    Test for the add_experiment view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that experimental
    conditions can be created and that the experimental condition's name cannot be
    duplicated.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.duplicate_experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition 1',
            description = 'This is a test experimental condition',
            experiment = self.experiment
        )


    def test_add_experiment_view_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        response = self.client.get(reverse('add_experimental_condition', kwargs={'experiment_name_slug': self.experiment.slug}))
        self.assertEqual(response.status_code, 200)


    def test_addition_of_new_experimental_condition(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/experiment.html'):
            response = self.client.post(reverse('add_experimental_condition', kwargs={'experiment_name_slug': self.experiment.slug}), {
                'name': 'Experimental Condition 1',
                'description': 'This is a test experimental condition',
                }
            )
        self.assertEqual(response.status_code, 200)
        experimental_condition = ExperimentalCondition.objects.get(name = 'Experimental Condition 1')
        self.assertTrue(isinstance(experimental_condition, ExperimentalCondition))


    def test_to_ensure_duplicate_experimental_condition_names_constraint_holds(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/add_experimental_condition.html'):
            response = self.client.post(reverse('add_experimental_condition', kwargs={'experiment_name_slug': self.experiment.slug}),
                {'name': 'Test Condition 1',
                'description': 'This is a test experimental condition',
                }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'experimental_condition_form', 'name', 'Experimental condition with this Name already exists.')


class ConditionSummaryViewTest(TestCase):
    """
    Test for the condition_summary view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition',
            description = 'This is a test condition',
            experiment = self.experiment
        )


    def test_condition_summary_page_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/condition.html'):
            self.client.get(reverse('condition_summary', kwargs={
                'experiment_name_slug': self.experiment.slug,
                'condition_name_slug': self.experimental_condition.slug
            }))


class AddSampleViewTest(TestCase):
    """
    Test for the add_sample view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that samples
    can be created and that the sample's name cannot be duplicated.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition 1',
            description = 'This is a test experimental condition',
            experiment = self.experiment
        )
        self.duplicate_sample = Sample.objects.create(
            name = 'Test Sample 1',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'testorganism',
        )


    def test_add_experiment_view_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        response = self.client.get(reverse('add_sample', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug}))
        self.assertEqual(response.status_code, 200)


    def test_addition_of_new_experimental_sample(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/condition.html'):
            response = self.client.post(reverse('add_sample', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug}), {
                'name': 'Sample 1',
                'description': 'This is a test sample',
                }
            )
        self.assertEqual(response.status_code, 200)
        sample = Sample.objects.get(name = 'Sample 1')
        self.assertTrue(isinstance(sample, Sample))


    def test_to_ensure_duplicate_experimental_sample_names_constraint_holds(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/add_sample.html'):
            response = self.client.post(reverse('add_sample', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug}),
                {'name': 'Test Sample 1',
                'description': 'This is a test sample',
                }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'sample_form', 'name', 'Sample with this Name already exists.')


class AddSampleFileViewTest(TestCase):
    """
    Test for the add_sample_file view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that sample files
    can be uploaded and that the sample file names cannot be duplicated. Finally,
    we also want to ensure that only 'mzXML' files can be uploaded at present.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition 1',
            description = 'This is a test experimental condition',
            experiment = self.experiment
        )
        self.sample = Sample.objects.create(
            name = 'Test Sample 1',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'testorganism',
        )
        self.file_for_upload_filepath = os.path.join(
            BASE_DIR,
            'frank',
            'TestingFiles',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        self.invalid_file_for_upload_filepath = os.path.join(
            BASE_DIR,
            'frank',
            'TestingFiles',
            'Invalid.txt',
        )
        ### Ensure the file to be uploaded doesn't already exist at the beginning of the tests
        proposed_upload_path = os.path.join(
            MEDIA_ROOT,
            'frank',
            self.user.username,
            self.experiment.slug,
            self.experimental_condition.slug,
            self.sample.slug,
            'Negative',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        try:
            ## Ensure the test file doesn't exist at the start of each test
            ## or upload with fail.
            os.remove(str(proposed_upload_path))
        except OSError:
            pass


    def test_add_sample_file_view_renders_for_authenticated_user(self):
        self.client.login(username='testrunner', password='password')
        response = self.client.get(reverse('add_sample_file', kwargs={
            'experiment_name_slug': self.experiment.slug,
            'condition_name_slug': self.experimental_condition.slug,
            'sample_slug': self.sample.slug
        }))
        self.assertEqual(response.status_code, 200)


    def test_addition_of_new_sample_file(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/condition.html') \
                and open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.assertEqual(response.status_code, 200)
        sample_file = SampleFile.objects.get(name = 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        self.assertTrue(isinstance(sample_file, SampleFile))
        try:
            ## Remember to remove the uploaded file upon completion of the test
            os.remove(str(sample_file.address))
        except OSError:
            pass


    def test_to_ensure_duplicate_sample_files_cannot_be_uploaded_to_same_sample(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/condition.html') \
                and open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.assertEqual(response.status_code, 200)
        sample_file = SampleFile.objects.get(name = 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        # Then try and add the same sample file again
        with self.assertTemplateUsed(template_name='frank/add_sample_file.html') \
                and open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'sampleFileForm', 'address', 'This file already exists in the sample.')
        try:
            ## Remember to remove the uploaded file upon completion of the test
            os.remove(str(sample_file.address))
        except OSError:
            pass


    def test_to_ensure_invalid_file_formats_cannot_be_uploaded(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/add_sample_file.html') \
                and open(self.invalid_file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'sampleFileForm', 'address', 'Incorrect file format. Please upload an mzXML file')


class CreateFragmentationSetViewTest(TestCase):
    """
    Test for the create_fragmentation_set view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that fragmentation sets
    can be create and that fragmentation sets have a unique name. Finally,
    we also want to ensure that fragmentation sets can only be created for experiments
    with at least one sample file.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition 1',
            description = 'This is a test experimental condition',
            experiment = self.experiment
        )
        self.sample = Sample.objects.create(
            name = 'Test Sample 1',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'testorganism',
        )
        self.file_for_upload_filepath = os.path.join(
            BASE_DIR,
            'frank',
            'TestingFiles',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        ### Ensure the file to be uploaded doesn't already exist at the beginning of the tests
        proposed_upload_path = os.path.join(
            MEDIA_ROOT,
            'frank',
            self.user.username,
            self.experiment.slug,
            self.experimental_condition.slug,
            self.sample.slug,
            'Negative',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        try:
            ## Ensure the test file doesn't exist at the start of each test
            ## or upload with fail.
            os.remove(str(proposed_upload_path))
        except OSError:
            pass
        self.client.login(username='testrunner', password='password')
        with open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.sample_file = SampleFile.objects.get(name = 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        self.empty_experiment = Experiment.objects.create(
            title = 'Empty Test Experiment',
            description = 'This is a test experiment with no sample files',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.duplicate_fragmentation_set = FragmentationSet.objects.create(
            name = 'Duplicate Fragmentation Set',
            experiment = self.experiment,
        )


    def test_create_fragmentation_set_view_renders_for_authenticated_user(self):
        response = self.client.get(reverse('create_fragmentation_set', kwargs={
            'experiment_name_slug': self.experiment.slug,
        }))
        self.assertEqual(response.status_code, 200)


    def test_create_of_new_fragmentation_set(self):
        with self.assertTemplateUsed(template_name='frank/experiment.html'):
            response = self.client.post(reverse('create_fragmentation_set', kwargs={'experiment_name_slug': self.experiment.slug}), {
                'name': 'Test Fragmentation Set',
                }
            )
        self.assertEqual(response.status_code, 200)
        fragmentation_set = FragmentationSet.objects.get(name = 'Test Fragmentation Set')
        self.assertTrue(isinstance(fragmentation_set, FragmentationSet))


    def test_to_ensure_duplicate_names_for_fragmentation_sets_cannot_be_used(self):
        with self.assertTemplateUsed(template_name='frank/create_fragmentation_set.html'):
            response = self.client.post(reverse('create_fragmentation_set', kwargs={'experiment_name_slug': self.experiment.slug}), {
                'name': 'Duplicate Fragmentation Set',
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'frag_set_form', 'name', 'Fragmentation set with this Name already exists.')


    def test_to_ensure_fragmentation_sets_cannot_be_made_for_experiments_with_no_sample_files(self):
        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/create_fragmentation_set.html'):
            response = self.client.post(reverse('create_fragmentation_set', kwargs={'experiment_name_slug': self.empty_experiment.slug}), {
                'name': 'Test Fragmentation Set',
                }
            )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'frag_set_form', 'name', 'No source files found for experiment.')


class FragmentationSetSummaryViewTest(TestCase):
    """
    Test for the fragmentation_set_summary view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition 1',
            description = 'This is a test experimental condition',
            experiment = self.experiment
        )
        self.sample = Sample.objects.create(
            name = 'Test Sample 1',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'testorganism',
        )
        self.file_for_upload_filepath = os.path.join(
            BASE_DIR,
            'frank',
            'TestingFiles',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        proposed_upload_path = os.path.join(
            MEDIA_ROOT,
            'frank',
            self.user.username,
            self.experiment.slug,
            self.experimental_condition.slug,
            self.sample.slug,
            'Negative',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        try:
            ## Ensure the test file doesn't exist at the start of each test
            ## or upload with fail.
            os.remove(str(proposed_upload_path))
        except OSError:
            pass
        self.client.login(username='testrunner', password='password')
        with open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.sample_file = SampleFile.objects.get(name = 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        self.fragmentation_set = FragmentationSet.objects.create(
            name = 'Test Fragmentation Set',
            experiment = self.experiment
        )
        self.fragmentation_set2 = FragmentationSet.objects.create(
            name = 'Test Fragmentation Set 2',
            experiment = self.experiment
        )


    def test_fragmentation_set_summary_view_renders_for_authenticated_user(self):
        response = self.client.get(reverse('fragmentation_set_summary'))
        self.assertEqual(response.status_code, 200)


class FragmentationSetViewTest(TestCase):
    """
    Test for the fragmentation_set view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure all the available
    AnnotationTools can be selected for an annotation query.
    """

    def setUp(self):
        population_script.populate()
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition 1',
            description = 'This is a test experimental condition',
            experiment = self.experiment
        )
        self.sample = Sample.objects.create(
            name = 'Test Sample 1',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'testorganism',
        )
        self.file_for_upload_filepath = os.path.join(
            BASE_DIR,
            'frank',
            'TestingFiles',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        proposed_upload_path = os.path.join(
            MEDIA_ROOT,
            'frank',
            self.user.username,
            self.experiment.slug,
            self.experimental_condition.slug,
            self.sample.slug,
            'Negative',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        try:
            ## Ensure the test file doesn't exist at the start of each test
            ## or upload with fail.
            os.remove(str(proposed_upload_path))
        except OSError:
            pass
        self.client.login(username='testrunner', password='password')
        with open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.sample_file = SampleFile.objects.get(name = 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        self.fragmentation_set = FragmentationSet.objects.create(
            name = 'Test Fragmentation Set',
            experiment = self.experiment
        )
        parent_peak = None
        msn_Level = 1
        for peak_number in range(0, 50):
            my_test_peak = Peak.objects.create(
                source_file = self.sample_file,
                mass = 400-2*peak_number,
                retention_time = 400-2*peak_number,
                intensity = 10000-10*peak_number,
                parent_peak = parent_peak,
                fragmentation_set = self.fragmentation_set,
                msn_level = msn_Level
            )
            if peak_number % 10 == 0:
                parent_peak = my_test_peak
                msn_Level = msn_Level+1
        self.massbank = AnnotationTool.objects.get(name = "MassBank")
        self.nist = AnnotationTool.objects.get(name = "NIST")
        self.network_sampler = AnnotationTool.objects.get(name = 'LCMS DDA Network Sampler')



    def test_fragmentation_set_view_renders_for_authenticated_user(self):
        response = self.client.get(reverse('fragmentation_set', kwargs={
            'fragmentation_set_name_slug': self.fragmentation_set.slug,
        }))
        self.assertEqual(response.status_code, 200)


    def test_fragmentation_set_view_selection_of_massbank(self):
        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.post(reverse('fragmentation_set', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
            }), {
                'tool_selection': self.massbank.id
            })
        self.assertEqual(response.status_code, 200)


    def test_fragmentation_set_view_selection_of_nist(self):
        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.post(reverse('fragmentation_set', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
            }), {
                'tool_selection': self.nist.id
            })
        self.assertEqual(response.status_code, 200)


    def test_fragmentation_set_view_selection_of_network_sampler(self):
        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.post(reverse('fragmentation_set', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
            }), {
                'tool_selection': self.network_sampler.id
            })
        self.assertEqual(response.status_code, 200)


class PeakSummaryViewTest(TestCase):
    """
    Test for the peak_summary view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        population_script.populate()
        self.client = Client()
        self.user = User.objects.create_user(
            'testrunner',
            'testrunner@gmail.com',
            'password'
        )
        experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'ExperimentalProtocol 1'
        )
        self.experiment = Experiment.objects.create(
            title = 'Test Experiment',
            description = 'This is a test experiment',
            created_by = self.user,
            ionisation_method = 'EIS',
            detection_method = experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition 1',
            description = 'This is a test experimental condition',
            experiment = self.experiment
        )
        self.sample = Sample.objects.create(
            name = 'Test Sample 1',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'testorganism',
        )
        self.file_for_upload_filepath = os.path.join(
            BASE_DIR,
            'frank',
            'TestingFiles',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        proposed_upload_path = os.path.join(
            MEDIA_ROOT,
            'frank',
            self.user.username,
            self.experiment.slug,
            self.experimental_condition.slug,
            self.sample.slug,
            'Negative',
            'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
        )
        try:
            ## Ensure the test file doesn't exist at the start of each test
            ## or upload with fail.
            os.remove(str(proposed_upload_path))
        except OSError:
            pass
        self.client.login(username='testrunner', password='password')
        with open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse('add_sample_file', kwargs={'experiment_name_slug': self.experiment.slug, 'condition_name_slug': self.experimental_condition.slug,'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.sample_file = SampleFile.objects.get(name = 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        self.fragmentation_set = FragmentationSet.objects.create(
            name = 'Test Fragmentation Set',
            experiment = self.experiment
        )
        parent_peak = None
        msn_Level = 1
        for peak_number in range(0, 50):
            my_test_peak = Peak.objects.create(
                source_file = self.sample_file,
                mass = 400-2*peak_number,
                retention_time = 400-2*peak_number,
                intensity = 10000-10*peak_number,
                parent_peak = parent_peak,
                fragmentation_set = self.fragmentation_set,
                msn_level = msn_Level
            )
            if peak_number % 10 == 0:
                parent_peak = my_test_peak
                msn_Level = msn_Level+1
        self.massbank = AnnotationTool.objects.get(name = "MassBank")
        self.nist = AnnotationTool.objects.get(name = "NIST")
        self.network_sampler = AnnotationTool.objects.get(name = 'LCMS DDA Network Sampler')


    def test_peak_summary_view_renders_for_authenticated_user(self):
        peak_slug = Peak.objects.get(id=1).slug
        response = self.client.get(reverse('peak_summary', kwargs={
            'fragmentation_set_name_slug': self.fragmentation_set.slug,
            'peak_name_slug':peak_slug,
        }))
        self.assertEqual(response.status_code, 200)