from django.test import TestCase
from frank.models import *
from frank.forms import *
from frank.admin import *
from frank.views import *
from annotationTools import MassBankQueryTool
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils import unittest
from django.test.client import Client
from django.conf import settings
import os
from django.core.files import File
import populate_pimp as population_script
from peakFactories import MSNPeakBuilder, GCMSPeakBuilder, PeakBuilder
import rpy2.robjects as robjects
import rpy2.rlike.container as rlc
import mock
import re


"""
In order for the tests to run correctly, several methods have to initially
be created to create default objects in the database.
"""


def run_population_script():

    """
    Method to run the population script
    """

    population_script.populate(testing=True)


def create_test_user():

    """
    Method to create a user
    """

    try:
        user = User.objects.get_by_natural_key('testrunner')
    except ObjectDoesNotExist:
        user = User.objects.create_user(
            username='testrunner',
            email='testrunner@gmail.com',
            password='password'
        )
    return user


def create_logged_in_client():

    """
    Method to generate a logged in client, as all views have the @login_required
    """

    user = create_test_user()
    client = Client()
    client.login(username='testrunner', password='password')
    return client


def create_valid_lcms_experiment():

    """
    Method to create a valid lcms experiment
    """

    run_population_script()
    experimental_protocol = ExperimentalProtocol.objects.get_or_create(
        name='Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'
    )[0]
    user = create_test_user()
    experiment = Experiment.objects.get_or_create(
        title='Experiment LCMS',
        description='This is another experiment',
        created_by=user,
        ionisation_method='Electron Ionisation Spray',
        detection_method=experimental_protocol,
    )[0]
    return experiment


def create_valid_gcms_experiment():

    """
    Method to create a valid gcms experiment
    """

    run_population_script()
    experimental_protocol = ExperimentalProtocol.objects.get_or_create(
        name='Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation'
    )[0]
    user = create_test_user()
    experiment = Experiment.objects.get_or_create(
        title='Experiment GCMS',
        description='This is another experiment',
        created_by=user,
        ionisation_method='Electron Impact Ionisation',
        detection_method=experimental_protocol,
    )[0]
    return experiment


def create_experimental_condition():

    """
    Method to create a default experimental condition
    """

    experiment = create_valid_lcms_experiment()
    experimental_condition = ExperimentalCondition.objects.get_or_create(
        name='Test Condition 1',
        description='This is a test experimental condition',
        experiment=experiment
    )[0]
    return experimental_condition


def create_sample():

    """
    Method to create a default experimental sample
    """

    experimental_condition = create_experimental_condition()
    sample = Sample.objects.get_or_create(
        name='Test Sample 1',
        description='This is a test sample',
        experimental_condition=experimental_condition,
        organism='Sample Organism'
    )[0]
    return sample


def remove_previous_uploads(sample_object, polarity, file_name):

    """
    Method to remove a previously uploaded test file to ensure
    tests run as intended.
    """

    intended_upload_path = os.path.join(
        settings.MEDIA_ROOT,
        'frank',
        sample_object.experimental_condition.experiment.created_by.username,
        sample_object.experimental_condition.experiment.slug,
        sample_object.experimental_condition.slug,
        sample_object.slug,
        polarity,
        file_name,
    )
    try:
        os.remove(str(intended_upload_path))
    except OSError:
        pass
    return True


def create_lcms_test_experiment_with_files():

    """
    Method for creating a typical lcms experimental set-up
    """

    create_test_user()
    first_sample = create_sample()
    test_file1 = os.path.join(
        settings.BASE_DIR,
        'frank',
        'TestingFiles',
        'LCMS_Files',
        'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML',
    )
    test_file2 = os.path.join(
        settings.BASE_DIR,
        'frank',
        'TestingFiles',
        'LCMS_Files',
        'STD_MIX1_POS_60stepped_1E5_Top5.mzXML',
    )
    my_client = create_logged_in_client()
    upload_files = {}
    upload_files['file1'] = {'filepath': test_file1, 'polarity': 'Negative'}
    upload_files['file2'] = {'filepath': test_file2, 'polarity': 'Positive'}
    remove_previous_uploads(first_sample, 'Negative', 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
    remove_previous_uploads(first_sample, 'Positive', 'STD_MIX1_POS_60stepped_1E5_Top5.mzXML')

    for test_file in upload_files:
        with open(upload_files[test_file]['filepath']) as upload_file:
            response = my_client.post(reverse(
                'add_sample_file',
                kwargs={
                    'experiment_name_slug': first_sample.experimental_condition.experiment.slug,
                    'condition_name_slug': first_sample.experimental_condition.slug,
                    'sample_slug': first_sample.slug
                }), {
                'address': upload_file,
                'polarity': upload_files[test_file]['polarity'],
            })
    return first_sample.experimental_condition.experiment


def create_gcms_test_experiment_with_files():

    """
    Method for creating a typical gcms experimental set-up
    """

    create_test_user()
    experiment = create_valid_gcms_experiment()
    experimental_condition = ExperimentalCondition.objects.get_or_create(
        experiment=experiment,
        name='GCMSCondition',
    )[0]
    sample = Sample.objects.get_or_create(
        experimental_condition=experimental_condition,
        name='GCMSSample',
    )[0]
    test_file1 = os.path.join(
        settings.BASE_DIR,
        'frank',
        'TestingFiles',
        'GCMS_Files',
        'T0R1R.mzXML',
    )
    """
    Test File 2 can be added to provide an additional test case,
    however, the gcms test files are large and so one will suffice.
    """
    # test_file2 = os.path.join(
    #     BASE_DIR,
    #     'frank',
    #     'TestingFiles',
    #     'GCMS_Files',
    #     'T1R3L.mzXML',
    # )
    my_client = create_logged_in_client()
    upload_files = {}
    upload_files['file1'] = {'filepath': test_file1, 'polarity': 'Negative'}
    # upload_files['file2'] = {'filepath': test_file2, 'polarity': 'Positive'}
    remove_previous_uploads(sample, 'Positive', 'T0R1R.mzXML')
    remove_previous_uploads(sample, 'Positive', 'T1R3L.mzXML')

    for test_file in upload_files:
        with open(upload_files[test_file]['filepath']) as upload_file:
            response = my_client.post(reverse(
                'add_sample_file',
                kwargs={
                    'experiment_name_slug': sample.experimental_condition.experiment.slug,
                    'condition_name_slug': sample.experimental_condition.slug,
                    'sample_slug': sample.slug
                }), {
                'address': upload_file,
                'polarity': upload_files[test_file]['polarity'],
            })
    return sample.experimental_condition.experiment


def create_gcms_fragmentation_set():

    """
    Method to create a mock gcms fragmentation set
    """

    experiment = create_gcms_test_experiment_with_files()
    fragmentation_set = FragmentationSet.objects.get_or_create(
        name='GCMSFragSet',
        experiment=experiment,
        status='Completed Successfully'
    )[0]
    sample_files = SampleFile.objects.filter(
        sample__experimental_condition__experiment=experiment)
    for input_file in sample_files:
        pseudo_ms1_peak = Peak.objects.create(
            source_file=input_file,
            mass=73.0468,
            retention_time=867.4150,
            intensity=1481587.38,
            parent_peak=None,
            msn_level=1,
            fragmentation_set=fragmentation_set
        )
        for index in range(0, 10):
            Peak.objects.create(
                source_file=input_file,
                mass=pseudo_ms1_peak.mass-(index*4),
                retention_time=pseudo_ms1_peak.rentention_time-(index*10),
                intensity=pseudo_ms1_peak.intensity-(index*500),
                parent_peak=None,
                msn_level=2,
                fragmentation_set=fragmentation_set
            )
    return fragmentation_set


def create_lcms_fragmentation_set():

    """
    Method to create a mock lcms fragmentation set
    """

    experiment = create_lcms_test_experiment_with_files()
    fragmentation_set = FragmentationSet.objects.get_or_create(
        name='LCMSFragSet',
        experiment=experiment,
        status='Completed Successfully'
    )[0]
    sample_files = SampleFile.objects.filter(
        sample__experimental_condition__experiment=experiment)
    for input_file in sample_files:
        precursor_peak = Peak.objects.create(
            source_file=input_file,
            mass=137.0458,
            retention_time=515.4240,
            intensity=60518756.0000,
            parent_peak=None,
            msn_level=1,
            fragmentation_set=fragmentation_set
        )
        for index in range(0, 10):
            Peak.objects.create(
                source_file=input_file,
                mass=precursor_peak.mass-(index*10),
                retention_time=precursor_peak.retention_time-(index*20),
                intensity=precursor_peak.intensity-(index*1000),
                parent_peak=None,
                msn_level=2,
                fragmentation_set=fragmentation_set
            )
    return fragmentation_set

def add_genuine_spectrum(fragmentation_set):

    """
    Method to add a genuine spectrum to a fragmentation set
    """
    source_file = SampleFile.objects.filter(
            sample__experimental_condition__experiment=fragmentation_set.experiment
        )[0]
    parent_peak = Peak.objects.create(
        source_file=source_file,
        mass=109.0761,
        retention_time=302.2270,
        intensity=1559883.3750,
        parent_peak=None,
        msn_level=1,
        fragmentation_set=fragmentation_set
    )
    peak1 = Peak.objects.create(
        source_file=source_file,
        mass=65.0388,
        retention_time=300.3950,
        intensity=70030.99,
        parent_peak=parent_peak,
        msn_level=2,
        fragmentation_set=fragmentation_set
    )
    peak2 = Peak.objects.create(
        source_file=source_file,
        mass=67.0543,
        retention_time=300.3950,
        intensity=3235.91,
        parent_peak=parent_peak,
        msn_level=2,
        fragmentation_set=fragmentation_set
    )
    peak3 = Peak.objects.create(
        source_file=source_file,
        mass=80.0495,
        retention_time=300.3950,
        intensity=2457.76,
        parent_peak=parent_peak,
        msn_level=2,
        fragmentation_set=fragmentation_set
    )
    peak4 = Peak.objects.create(
        source_file=source_file,
        mass=82.0650,
        retention_time=300.3950,
        intensity=4333.99,
        parent_peak=parent_peak,
        msn_level=2,
        fragmentation_set=fragmentation_set
    )
    peak5 = Peak.objects.create(
        source_file=source_file,
        mass=92.0495,
        retention_time=300.3950,
        intensity=153425.52,
        parent_peak=parent_peak,
        msn_level=2,
        fragmentation_set=fragmentation_set
    )

"""
Views.py Tests - Mostly this consisted of testing the pages render. However, in the case of the
forms varying inputs have been checked to ensure errors are caught.

"""


class IndexTestView(TestCase):

    """
    These are tests for the index view of Frank, we want to test that the
    page renders and that the user who is not authenticated will be redirected
    to the login page (i.e. a test of the @login_required decorator)
    """

    def setUp(self):

        self.client = create_logged_in_client()

    def test_index_renders_for_authenticated_user(self):

        """
        Test to ensure page renders for authenticated user
        """

        response = self.client.get(reverse('frank_index'))
        self.assertEqual(response.status_code, 200)

    def test_index_with_non_authenticated_client(self):

        """
        Test to ensure page re-directs if the user is not authenticated.
        From this point on it is assumed the @login_required decorators work
        as anticipated.
        """

        client = Client()
        response = client.get(reverse('frank_index'))
        self.assertRedirects(response, 'accounts/login/?next=/frank/')


class MyExperimentsViewTest(TestCase):

    """
    Test for the my_experiments view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):

        self.client = create_logged_in_client()

    def test_my_experiment_view_renders_for_authenticated_user(self):

        """
        Test case to ensure the My Experiments page of the site renders
        """

        response = self.client.get(reverse('my_experiments'))
        self.assertEqual(response.status_code, 200)


class AddExperimentViewTest(TestCase):

    """
    Test for the add_experiment view in frank.views. Here we want to test that
    the page renders for an authenticated user. In additon, we want to test that
    the addition submission of a valid form creates an experiment object. Finally,
    we want to ensure that experiment titles cannot be duplicated as this will
    compromise the unique constraint on the experiment slug.
    """

    def setUp(self):

        self.client = create_logged_in_client()
        self.existing_experiment = create_valid_lcms_experiment()

    def test_add_experiment_view_renders_for_authenticated_user(self):

        """
        Method to test the rendering of the add experiment page
        """

        response = self.client.get(reverse('add_experiment'))
        self.assertEqual(response.status_code, 200)

    def test_addition_of_new_experiment(self):

        """
        Method to test the addition of a new experiment using a POST request
        creates a new object in the test database
        """

        with self.assertTemplateUsed(template_name='frank/my_experiments.html'):
            response = self.client.post(reverse('add_experiment'), {
                'title': 'Experiment 1',
                'description': 'This is a test experiment',
                'ionisation_method': 'ESI',
                'detection_method': '1'
            })
        self.assertEqual(response.status_code, 200)
        experiment = Experiment.objects.get(title='Experiment 1')
        self.assertTrue(isinstance(experiment, Experiment))

    def test_to_ensure_duplicate_experiment_titles_constraint_holds(self):

        """
        Method to test that the addition of a new experiment, duplicating the title
        of an existing experiment fails to create an experiment in the test database
        """

        with self.assertTemplateUsed(template_name='frank/add_experiment.html'):
            duplicated_title = self.existing_experiment.title
            description = 'This is the duplicated title'
            response = self.client.post(reverse('add_experiment'), {
                'title': duplicated_title,
                'description': description,
                'ionisation_method': 'Electron Ionisation Spray',
                'detection_method': '1'
            })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'experiment_form', 'title', 'Experiment with this Title already exists.')
        with self.assertRaises(ObjectDoesNotExist):
            Experiment.objects.get(title=duplicated_title, description=description)


class ExperimentSummaryViewTest(TestCase):

    """
    Test for the experiment summary view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):

        self.client = create_logged_in_client()
        self.experiment = create_valid_lcms_experiment()

    def test_experiment_summary_page_renders_for_authenticated_user(self):

        """
        Test to ensure the experiment summary page renders for an authenticated user
        """

        self.client.login(username='testrunner', password='password')
        with self.assertTemplateUsed(template_name='frank/experiment.html'):
            self.client.get(reverse('experiment_summary', kwargs={'experiment_name_slug': self.experiment.slug}))


class AddExperimentalConditionViewTest(TestCase):

    """
    Test for the add_experimental_condition view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that experimental
    conditions can be created and that the experimental condition's name cannot be
    duplicated.
    """

    def setUp(self):

        self.client = create_logged_in_client()
        self.experiment = create_valid_lcms_experiment()
        self.existing_experimental_condition = create_experimental_condition()

    def test_add_experimental_condition_view_renders_for_authenticated_user(self):

        """
        Test to ensure the Experiment page of the application renders
        """

        response = self.client.get(reverse(
            'add_experimental_condition', kwargs={'experiment_name_slug': self.experiment.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_addition_of_new_experimental_condition(self):

        """
        Test to check the addition of a new experimental condition
        """

        with self.assertTemplateUsed(template_name='frank/experiment.html'):
            name = 'New Experimental Condition'
            response = self.client.post(reverse(
                'add_experimental_condition',
                kwargs={'experiment_name_slug': self.experiment.slug}), {
                'name': name,
                'description': 'This is a test experimental condition',
            })
        self.assertEqual(response.status_code, 200)
        experimental_condition = ExperimentalCondition.objects.get(name=name)
        self.assertTrue(isinstance(experimental_condition, ExperimentalCondition))

    def test_to_ensure_duplicate_experimental_condition_names_constraint_holds(self):

        """
        Test to check that the addition of a new experimental condition cannot duplicate
        that of an existing experimental condition.
        """

        with self.assertTemplateUsed(template_name='frank/add_experimental_condition.html'):
            duplicate_name = self.existing_experimental_condition.name
            duplicate_description = 'This is a duplicate experimental condition'
            response = self.client.post(reverse(
                'add_experimental_condition',
                kwargs={'experiment_name_slug': self.experiment.slug}), {
                'name': duplicate_name,
                'description': duplicate_description,
            })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'experimental_condition_form', 'name',
                             'Experimental condition with this Name already exists.')
        with self.assertRaises(ObjectDoesNotExist):
            Experiment.objects.get(title=duplicate_name, description=duplicate_description)


class ConditionSummaryViewTest(TestCase):

    """
    Test for the condition_summary view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        self.client = create_logged_in_client()
        self.experimental_condition = create_experimental_condition()

    def test_condition_summary_page_renders_for_authenticated_user(self):

        """
        Method to test that the experimental condition summary page renders for authenticated user
        """

        with self.assertTemplateUsed(template_name='frank/condition.html'):
            self.client.get(reverse('condition_summary', kwargs={
                'experiment_name_slug': self.experimental_condition.experiment.slug,
                'condition_name_slug': self.experimental_condition.slug
            }))


class AddSampleViewTest(TestCase):

    """
    Test for the add_sample view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that samples
    can be created and that the sample's name cannot be duplicated.
    """

    def setUp(self):
        self.client = create_logged_in_client()
        self.duplicate_sample = create_sample()

    def test_add_sample_view_renders_for_authenticated_user(self):

        """
        Test to ensure the page renders successfully for the authenticated client
        """

        response = self.client.get(reverse(
            'add_sample',
            kwargs={
                'experiment_name_slug': self.duplicate_sample.experimental_condition.experiment.slug,
                'condition_name_slug': self.duplicate_sample.experimental_condition.slug}
        ))
        self.assertEqual(response.status_code, 200)

    def test_addition_of_new_experimental_sample(self):

        """
        Test to ensure the submission of a new experimental sample is added to the database
        """

        with self.assertTemplateUsed(template_name='frank/condition.html'):
            sample_name = 'Additional Sample'
            sample_description = 'The submitted sample'
            response = self.client.post(reverse(
                'add_sample', kwargs={
                    'experiment_name_slug': self.duplicate_sample.experimental_condition.experiment.slug,
                    'condition_name_slug': self.duplicate_sample.experimental_condition.slug
                }), {
                'name': sample_name,
                'description': sample_description,
                }
            )
        self.assertEqual(response.status_code, 200)
        sample = Sample.objects.get(name=sample_name)
        self.assertTrue(isinstance(sample, Sample))

    def test_to_ensure_duplicate_experimental_sample_names_constraint_holds(self):

        """
        Test to ensure that attempts to add new experimental samples with identical names
        generates for errors and does not add the sample to the database
        """

        with self.assertTemplateUsed(template_name='frank/add_sample.html'):
            duplicate_sample_name = self.duplicate_sample.name
            duplicate_sample_description = 'This is the duplicated sample'
            response = self.client.post(reverse(
                'add_sample', kwargs={
                    'experiment_name_slug': self.duplicate_sample.experimental_condition.experiment.slug,
                    'condition_name_slug': self.duplicate_sample.experimental_condition.slug}), {
                'name': duplicate_sample_name,
                'description': duplicate_sample_description}
            )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'sample_form', 'name', 'Sample with this Name already exists.')
        with self.assertRaises(ObjectDoesNotExist):
            Sample.objects.get(name=duplicate_sample_name, description=duplicate_sample_description)


class AddSampleFileViewTest(TestCase):

    """
    Test for the add_sample_file view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that sample files
    can be uploaded and that the sample file names cannot be duplicated. Finally,
    we also want to ensure that only 'mzXML' files can be uploaded at present.
    """

    def setUp(self):
        self.client = create_logged_in_client()
        self.sample = create_sample()
        # These should correspond to two files in the TestingFiles folder
        self.file_name_valid = 'STD_MIX1_NEG_60stepped_1E5_Top5.mzXML'
        self.file_name_invalid = 'Invalid.txt'
        # Determine the paths for the test files to be uploaded
        self.file_for_upload_filepath = os.path.join(
            settings.BASE_DIR,
            'frank',
            'TestingFiles',
            self.file_name_valid,
        )
        self.invalid_file_for_upload_filepath = os.path.join(
            settings.BASE_DIR,
            'frank',
            'TestingFiles',
            self.file_name_invalid,
        )
        # Ensure these files haven't been uploaded to the sample folder by a previous test
        remove_previous_uploads(self.sample, 'Negative', self.file_name_valid)
        remove_previous_uploads(self.sample, 'Negative', self.file_name_invalid)

    def test_add_sample_file_view_renders_for_authenticated_user(self):

        """
        Method to test the add sample file page renders for the authenticated user
        """

        response = self.client.get(reverse('add_sample_file', kwargs={
            'experiment_name_slug': self.sample.experimental_condition.experiment.slug,
            'condition_name_slug': self.sample.experimental_condition.slug,
            'sample_slug': self.sample.slug
        }))
        self.assertEqual(response.status_code, 200)

    def test_addition_of_new_sample_file(self):

        """
        Method to test the addition of a new sample file via a POST request
        """

        with self.assertTemplateUsed(template_name='frank/condition.html') \
                and open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse(
                'add_sample_file',
                kwargs={'experiment_name_slug': self.sample.experimental_condition.experiment.slug,
                        'condition_name_slug': self.sample.experimental_condition.slug,
                        'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                }
            )
        self.assertEqual(response.status_code, 200)
        sample_file = SampleFile.objects.get(name='STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        self.assertTrue(isinstance(sample_file, SampleFile))

    def test_to_ensure_duplicate_sample_files_cannot_be_uploaded_to_same_sample(self):

        """
        Method to ensure duplicate sample files cannot be uploaded to the same sample
        """

        # Perform the first upload
        with self.assertTemplateUsed(template_name='frank/condition.html') \
                and open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse(
                'add_sample_file',
                kwargs={'experiment_name_slug': self.sample.experimental_condition.experiment.slug,
                        'condition_name_slug': self.sample.experimental_condition.slug,
                        'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                })
        self.assertEqual(response.status_code, 200)
        sample_file = SampleFile.objects.get(name='STD_MIX1_NEG_60stepped_1E5_Top5.mzXML')
        self.assertTrue(sample_file, SampleFile)
        # Then try and add the same sample file again
        with self.assertTemplateUsed(template_name='frank/add_sample_file.html') \
                and open(self.file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse(
                'add_sample_file',
                kwargs={
                    'experiment_name_slug': self.sample.experimental_condition.experiment.slug,
                    'condition_name_slug': self.sample.experimental_condition.slug,
                    'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'sample_file_form', 'address', 'This file already exists in the sample.')

    def test_to_ensure_invalid_file_formats_cannot_be_uploaded(self):

        """
        Method to ensure that invalid file formats cannot be uploaded
        """

        with self.assertTemplateUsed(template_name='frank/add_sample_file.html') \
                and open(self.invalid_file_for_upload_filepath) as upload_file:
            response = self.client.post(reverse(
                'add_sample_file',
                kwargs={
                    'experiment_name_slug': self.sample.experimental_condition.experiment.slug,
                    'condition_name_slug': self.sample.experimental_condition.slug,
                    'sample_slug': self.sample.slug}), {
                'address': upload_file,
                'polarity': 'Negative',
                })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'sample_file_form',
            'address',
            'Incorrect file format. Please upload an mzXML file'
        )


class CreateFragmentationSetViewTest(TestCase):
    """
    Test for the create_fragmentation_set view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure that fragmentation sets
    can be create and that fragmentation sets have a unique name. In addition, we want
    to test that the creation of a fragmentation set works for both gcms and lcms. Finally,
    we also want to ensure that fragmentation sets can only be created for experiments
    with at least one sample file.
    """

    def setUp(self):
        self.client = create_logged_in_client()
        self.user = create_test_user()
        self.lcms_experiment = create_lcms_test_experiment_with_files()
        self.gcms_experiment = create_gcms_test_experiment_with_files()

    def test_create_fragmentation_set_view_renders_for_authenticated_user(self):

        """
        Method to test the create fragmentation set view renders for the authorised user
        """

        response = self.client.get(reverse('create_fragmentation_set', kwargs={
            'experiment_name_slug': self.lcms_experiment.slug,
        }))
        self.assertEqual(response.status_code, 200)

        """
        The following tests have been commented out, due to the duration of time required
        to run them. However, these can be uncommented for complete testing of the background
        processes.
        """

    # def test_create_of_new_lcms_fragmentation_set(self):
    #
    #     """
    #     Method to test the submission of a valid LCMS experiment generates a new fragmentation set
    #     which is populated with peaks.
    #     """
    #
    #     with self.assertTemplateUsed(template_name='frank/experiment.html'):
    #         response = self.client.post(reverse(
    #             'create_fragmentation_set', kwargs={'experiment_name_slug': self.lcms_experiment.slug}), {
    #             'name': 'Test LCMS Fragmentation Set',
    #         })
    #     self.assertEqual(response.status_code, 200)
    #     fragmentation_set = FragmentationSet.objects.get(name = 'Test LCMS Fragmentation Set')
    #     self.assertTrue(isinstance(fragmentation_set, FragmentationSet))
    #     new_fragmentation_set_peaks = Peak.objects.filter(fragmentation_set=fragmentation_set)
    #     self.assertTrue(len(new_fragmentation_set_peaks) > 0)
    #
    # def test_create_of_new_gcms_fragmentation_set(self):
    #
    #     """
    #     Method to test the submission of a valid GCMS experiment generates a new fragmentation set
    #     which is populated with peaks.
    #     """
    #
    #     with self.assertTemplateUsed(template_name='frank/experiment.html'):
    #         response = self.client.post(reverse(
    #             'create_fragmentation_set', kwargs={'experiment_name_slug': self.gcms_experiment.slug}), {
    #             'name': 'Test GCMS Fragmentation Set',
    #         })
    #     self.assertEqual(response.status_code, 200)
    #     fragmentation_set = FragmentationSet.objects.get(name = 'Test GCMS Fragmentation Set')
    #     self.assertTrue(isinstance(fragmentation_set, FragmentationSet))
    #     new_fragmentation_set_peaks = Peak.objects.filter(fragmentation_set=fragmentation_set)
    #     self.assertTrue(len(new_fragmentation_set_peaks) > 0)

    def test_to_ensure_duplicate_names_for_fragmentation_sets_cannot_be_used(self):

        """
        Method to test that the unique name constraint of the fragmentation set holds
        """

        duplicate_fragmentation_set = FragmentationSet.objects.create(
            name='Duplicate Fragmentation Set',
            experiment=self.lcms_experiment,
        )
        with self.assertTemplateUsed(template_name='frank/create_fragmentation_set.html'):
            response = self.client.post(reverse(
                'create_fragmentation_set', kwargs={'experiment_name_slug': self.lcms_experiment.slug}), {
                'name': 'Duplicate Fragmentation Set',
            })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'frag_set_form', 'name', 'Fragmentation set with this Name already exists.')

    def test_to_ensure_fragmentation_sets_cannot_be_made_for_experiments_with_no_sample_files(self):

        """
        Method to test that a fragmentation set cannot be created when no sample files are uploaded to the experiment
        """

        empty_experiment = Experiment.objects.create(
            title='Empty Test Experiment',
            description='This is a test experiment with no sample files',
            created_by=self.user,
            ionisation_method='EIS',
            detection_method=self.lcms_experiment.detection_method,
        )
        with self.assertTemplateUsed(template_name='frank/create_fragmentation_set.html'):
            response = self.client.post(reverse(
                'create_fragmentation_set', kwargs={'experiment_name_slug': empty_experiment.slug}), {
                'name': 'Test Fragmentation Set',
            })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'frag_set_form', 'name', 'No source files found for experiment.')

        """
        As before, these tests take significant time to run and as such have been commented out.
        However, these can be included for completeness of testing. At present they demonstrate
        the inability of the application to distinguish between GCMS and LCMS MS/MS datasets.
        """

    # def test_upload_of_data_files_which_correspond_to_the_wrong_experimental_protocol(self):
    #
    #     """
    #     Method to test that the upload of the incorrect data files is not permitted
    #     """
    #
    #     # By changing the LCMS experiment to the GCMS experimental protocol, the mzXML correspond to the wrong
    #     # experiment type
    #     self.lcms_experiment.detection_method = ExperimentalProtocol.objects.get(
    #             name='Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation'
    #     )
    #     self.lcms_experiment.save()
    #     with self.assertTemplateUsed(template_name='frank/experiment.html'):
    #         response = self.client.post(reverse(
    #             'create_fragmentation_set', kwargs={'experiment_name_slug': self.lcms_experiment.slug}), {
    #             'name': 'Test GCMS Files In LCMS Experiment',
    #         })
    #     self.assertEqual(response.status_code, 200)
    #     fragmentation_set = FragmentationSet.objects.get(name = 'Test GCMS Files In LCMS Experiment')
    #     self.assertTrue(isinstance(fragmentation_set, FragmentationSet))
    #     new_fragmentation_set_peaks = Peak.objects.filter(fragmentation_set=fragmentation_set)
    #     # The program shouldn't process these files, but it does
    #     self.assertFalse(len(new_fragmentation_set_peaks) > 0)
    #
    #
    #     # By changing the GCMS experiment to the LCMS experimental protocol, the mzXML correspond to the wrong
    #     # experiment type
    #     self.gcms_experiment.detection_method = ExperimentalProtocol.objects.get(
    #             name='Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'
    #     )
    #     self.gcms_experiment.save()
    #     with self.assertTemplateUsed(template_name='frank/experiment.html'):
    #         response = self.client.post(reverse(
    #             'create_fragmentation_set', kwargs={'experiment_name_slug': self.gcms_experiment.slug}), {
    #             'name': 'Test LCMS Files In GCMS Experiment',
    #         })
    #     self.assertEqual(response.status_code, 200)
    #     fragmentation_set = FragmentationSet.objects.get(name='Test LCMS Files In GCMS Experiment')
    #     self.assertTrue(isinstance(fragmentation_set, FragmentationSet))
    #     new_fragmentation_set_peaks = Peak.objects.filter(fragmentation_set=fragmentation_set)
    #     # The program shouldn't process these files, but it does
    #     self.assertFalse(len(new_fragmentation_set_peaks) > 0)


class FragmentationSetSummaryViewTest(TestCase):
    """
    Test for the fragmentation_set_summary view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        self.client = create_logged_in_client()

    def test_fragmentation_set_summary_view_renders_for_authenticated_user(self):

        """
        Method to ensure the fragmentation set summary page renders for the authenticated user
        """

        response = self.client.get(reverse('fragmentation_set_summary'))
        self.assertEqual(response.status_code, 200)


class FragmentationSetViewTest(TestCase):
    """
    Test for the fragmentation_set view in frank.views. Here we want to test that
    the page renders for an authenticated user. We also want to ensure all the available
    AnnotationTools can be selected for an annotation query.
    """

    def setUp(self):
        self.client = create_logged_in_client()
        self.lcms_fragmentation_set = create_lcms_fragmentation_set()

    def test_fragmentation_set_view_renders_for_authenticated_user(self):

        """
        Method to test that the fragmentation set page renders for authenticated user
        """
        response = self.client.get(reverse('fragmentation_set', kwargs={
            'fragmentation_set_name_slug': self.lcms_fragmentation_set.slug,
        }))
        self.assertEqual(response.status_code, 200)

    def test_fragmentation_set_view_selection_of_massbank(self):

        """
        Method to test selection of 'Massbank' from the fragmentation set page
        """

        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.post(reverse('fragmentation_set', kwargs={
                'fragmentation_set_name_slug': self.lcms_fragmentation_set.slug,
            }), {
                'tool_selection': AnnotationTool.objects.get(name='MassBank').id
            })
        self.assertEqual(response.status_code, 200)

    def test_fragmentation_set_view_selection_of_nist(self):

        """
        Method to test selection of 'NIST' from the fragmentation set page
        """

        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.post(reverse('fragmentation_set', kwargs={
                'fragmentation_set_name_slug': self.lcms_fragmentation_set.slug,
            }), {
                'tool_selection': AnnotationTool.objects.get(name='NIST').id
            })
        self.assertEqual(response.status_code, 200)


class PeakSummaryViewTest(TestCase):

    """
    Test for the peak_summary view in frank.views. Here we want to test that
    the page renders for an authenticated user.
    """

    def setUp(self):
        self.client = create_logged_in_client()
        self.fragmentation_set = create_lcms_fragmentation_set()
        self.peak = Peak.objects.filter(fragmentation_set=self.fragmentation_set)[0]

    def test_peak_summary_view_renders_for_authenticated_user(self):

        """
        Method to test that the peak summary page renders for authenticated users
        """

        peak_slug = self.peak.slug
        response = self.client.get(reverse('peak_summary', kwargs={
            'fragmentation_set_name_slug': self.fragmentation_set.slug,
            'peak_name_slug': peak_slug,
        }))
        self.assertEqual(response.status_code, 200)


class DefineAnnotationQueryViewTest(TestCase):

    """
    Test for the define_annotation_query view in frank.views. Here we want to test that
    the page renders for the selection of all three currently available annotation tools.
    In addition, we want to ensure the submission of valid parameters for each of the
    annotation tools generates valid candidate annotations.
    """

    def setUp(self):
        self.client = create_logged_in_client()
        self.fragmentation_set = create_lcms_fragmentation_set()
        self.massbank = AnnotationTool.objects.get(name='MassBank')
        self.nist = AnnotationTool.objects.get(name='NIST')
        self.precursormz = AnnotationTool.objects.get(name='Precursor Mass Filter')
        # To ensure genuine candidates can be found, the spectrum
        # for a peak is added
        add_genuine_spectrum(self.fragmentation_set)

    def test_define_annotation_query_view_renders_for_authenticated_user(self):

        """
        Method to test that the define annotation query view renders for each of
        the three annotation tools which may be selected.
        """

        # Check for Massbank tool
        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.get(reverse('define_annotation_query', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'annotation_tool_slug': self.massbank.slug,
            }))
        self.assertEqual(response.status_code, 200)

        # Check for NIST tool
        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.get(reverse('define_annotation_query', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'annotation_tool_slug': self.nist.slug,
            }))
        self.assertEqual(response.status_code, 200)

        # Check for Precursormz tool
        with self.assertTemplateUsed(template_name='frank/define_annotation_query.html'):
            response = self.client.get(reverse('define_annotation_query', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'annotation_tool_slug': self.precursormz.slug,
            }))
        self.assertEqual(response.status_code, 200)


    def test_define_annotation_query_view_generates_nist_annotations(self):

        """
        Method to test that the submission of valid parameters to the define
        annotation query view generates annotations from NIST.
        """

        with self.assertTemplateUsed(template_name='frank/fragmentation_set.html'):
            response = self.client.post(reverse('define_annotation_query', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'annotation_tool_slug': self.nist.slug,
            }), {
                'name': 'NIST Test Annotations',
                'maximum_number_of_hits': 5,
                'search_type': 'G',
                'query_libraries': ['nist_msms', 'nist_msms2'],
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(CandidateAnnotation.objects.all()) > 0)


    # def test_define_annotation_query_view_generates_massbank_annotations(self):
    #
    #     """
    #     Method to test that the submission of valid parameters to the define
    #     annotation query view generates annotations from MassBank.
    #
    #     This test has been commented out due to the temporary suspension of the service
    #     """
    #
    #     with self.assertTemplateUsed(template_name='frank/fragmentation_set.html'):
    #         response = self.client.post(reverse('define_annotation_query', kwargs={
    #             'fragmentation_set_name_slug': self.fragmentation_set.slug,
    #             'annotation_tool_slug': self.massbank.slug,
    #         }), {
    #             'name': 'Massbank Test Annotations',
    #             'massbank_instrument_types': ['LC-ESI-IT', 'LC-ESI-ITFT'],
    #         })
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(len(CandidateAnnotation.objects.all()) > 0)


    def test_define_annotation_query_view_generates_precursormz_annotations(self):

        """
        Method to test that the submission of valid parameters to the define
        annotation query view generates annotations using the PrecursorMz tool.
        """

        # First a populated Annotation Query must be made
        with self.assertTemplateUsed(template_name='frank/fragmentation_set.html'):
            response = self.client.post(reverse('define_annotation_query', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'annotation_tool_slug': self.nist.slug,
            }), {
                'name': 'NIST Test Annotations',
                'maximum_number_of_hits': 5,
                'search_type': 'G',
                'query_libraries': ['nist_msms', 'nist_msms2'],
            })
        nist_parent_query = AnnotationQuery.objects.get(name='NIST Test Annotations')

        with self.assertTemplateUsed(template_name='frank/fragmentation_set.html'):
            response = self.client.post(reverse('define_annotation_query', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'annotation_tool_slug': self.precursormz.slug,
            }), {
                'name': 'PrecursorMzTest',
                'parent_annotation_queries': [nist_parent_query.slug],
                'positive_transforms': ['M+H'],
                'mass_tol': 5,
            })
        self.assertEqual(response.status_code, 200)
        precursormz_query = AnnotationQuery.objects.get(name='PrecursorMzTest')
        self.assertTrue(len(CandidateAnnotation.objects.filter(annotation_query=precursormz_query)) > 0)


class SpecifyPreferredCandidateAnnotationViewTest(TestCase):

    """
    Test for the specify_preferred_annotation view in frank.views. Here we want to test that
    the page renders and that submission of the preferred annotation updates the Peak instance.
    """

    def setUp(self):
        self.fragmentation_set = create_lcms_fragmentation_set()
        add_genuine_spectrum(self.fragmentation_set)
        self.client = create_logged_in_client()
        self.peak = Peak.objects.filter(fragmentation_set=self.fragmentation_set)[0]
        self.massbank = AnnotationTool.objects.get(name='MassBank')
        self.annotation_query = AnnotationQuery.objects.get_or_create(
            name='testquery',
            fragmentation_set=self.fragmentation_set,
            annotation_tool=self.massbank,
        )[0]
        self.compound = Compound.objects.get_or_create(
            name='Glycine',
            formula='C4H8',
            exact_mass=123.456,
        )[0]
        self.annotation = CandidateAnnotation.objects.get_or_create(
            compound=self.compound,
            peak=self.peak,
            confidence=0.81,
            annotation_query=self.annotation_query,
            mass_match=False,
            adduct='M+H',
            difference_from_peak_mass=1.07,
        )[0]
        self.user = create_test_user()

    def test_specify_preferred_annotation_view_renders_for_authenticated_user(self):

        """
        Test to ensure the preferred annotation page of the application renders for the
        authenticated user.
        """

        with self.assertTemplateUsed(template_name='frank/specify_preferred_annotation.html'):
            response = self.client.get(reverse('specify_preferred_annotation', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'peak_name_slug': self.peak.slug,
                'annotation_id': self.annotation.id,
            }))
        self.assertEqual(response.status_code, 200)

    def test_specify_preferred_annotation_view_updates_peak(self):

        """
        Test to ensure the preferred annotation page of the application updates the
        Peak object upon submission of the form
        """

        with self.assertTemplateUsed(template_name='frank/peak_summary.html'):
            response = self.client.post(reverse('specify_preferred_annotation', kwargs={
                'fragmentation_set_name_slug': self.fragmentation_set.slug,
                'peak_name_slug': self.peak.slug,
                'annotation_id': self.annotation.id,
            }), {
                'preferred_candidate_description': 'This is my justification',
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(self.peak.preferred_candidate_annotation, CandidateAnnotation))


class PeakBuilderTests(TestCase):

    """
    Test class to ensure 'Abstract' Peak Builder cannot be instantiated
    """

    def test_peakBuilder_creation_throws_exception(self):

        """
        Test to ensure abstract class "PeakBuilder" cannot be instantiated
        """

        self.assertRaises(TypeError, PeakBuilder)


class MSNPeakBuilderTests(TestCase):

    """
    Test class for the testing of the MSNPeakBuilderClass
    """

    def setUp(self):

        """
        Set up of testing parameters
        """

        self.fragmentation_set = create_lcms_fragmentation_set()
        self.sample_file = SampleFile.objects.filter(
            sample__experimental_condition__experiment=self.fragmentation_set.experiment
        )[0]
        string_factor_filenames = robjects.StrVector((
            self.sample_file.name, self.sample_file.name, self.sample_file.name,
            self.sample_file.name, self.sample_file.name, self.sample_file.name
        ))
        factor_vector_filenames = string_factor_filenames.factor()
        peak_ID_vector = robjects.IntVector((1, 2, 3, 4, 5, 6))
        msn_parent_peak_ID_vector = robjects.IntVector((0, 1, 1, 1, 2, 0))
        ms_level_vector = robjects.IntVector((1, 2, 2, 2, 3, 1))
        rt_vector = robjects.FloatVector((100.1, 100.1, 100.1, 100.1, 100.1, 127.7))
        mz_vector = robjects.FloatVector((222.2, 101.1, 78.9, 65.5, 50.0, 280.1))
        intensity_vector = robjects.FloatVector((2220.2, 1010.1, 780.9, 650.5, 200.1, 2100.1))
        sample_vector = robjects.IntVector((1, 1, 1, 1, 1, 1))
        group_peak_vector = robjects.IntVector((0, 0, 0, 0, 0, 0))
        collision_energy_vector = robjects.IntVector((1, 1, 1, 1, 1, 1))
        valid_data = rlc.OrdDict([
            ('peakID', peak_ID_vector),
            ('MSnParentPeakID', msn_parent_peak_ID_vector),
            ('msLevel', ms_level_vector),
            ('rt', rt_vector),
            ('mz', mz_vector),
            ('intensity', intensity_vector),
            ('Sample', sample_vector),
            ('GroupPeakMSN', group_peak_vector),
            ('CollisionEnergy', collision_energy_vector),
            ('SourceFile', factor_vector_filenames),
        ])
        self.valid_r_dataframe_input = robjects.DataFrame(valid_data)
        self.valid_fragmentation_set_id_input = self.fragmentation_set.id


    def test_MSNPeakBuilder_init_valid_parameters_supplied(self):

        """
        Test that MSNPeakBuilder can be instantiated with valid parameters
        """

        self.assertTrue(isinstance(
            MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input), MSNPeakBuilder)
        )

    def test_createAPeak_valid_parameters(self):

        """
        Test that createAPeak creates new Peak model instance when passed valid parameters
        """

        peak_array_index = 2
        parent_peak_object = Peak.objects.filter(fragmentation_set=self.fragmentation_set)[0]
        peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
        self.assertTrue(isinstance(peak_builder_object._create_a_ms1_peak(peak_array_index, parent_peak_object), Peak))

    def test_getParentPeak(self):

        """
        Test that getParentPeak returns the precursor peak of a given fragment
        """

        peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
        parent_id_from_r = 2
        # Ensure the parent peak is created
        parent_peak = peak_builder_object._get_parent_peak(parent_id_from_r)
        self.assertTrue(isinstance(parent_peak, Peak))
        # Also check that the parent peak's precursor was created
        self.assertTrue(isinstance(parent_peak.parent_peak, Peak))

    def test_populate_database_peaks(self):

        """
        Test to ensure that populate_database_peaks does not throw any errors
        """

        peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
        peak_builder_object.populate_database_peaks()
        peak_query_set = Peak.objects.filter(fragmentation_set=self.fragmentation_set)
        # Check all test peaks with fragments have been created - using test data m/z to identify them
        self.assertTrue(isinstance(peak_query_set.get(mass=222.2), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=101.1), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=78.9), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=65.5), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=50.0), Peak))
        # The final test peak should not be created as it has no associated fragments or parent ion,
        # therefore is of no interest
        with self.assertRaises(ObjectDoesNotExist):
            peak_query_set.get(mass=280.1)


class MassBankQueryToolTests(TestCase):

    """
    Test Class for the testing of the MassBankQueryTool
    """

    def setUp(self):
        run_population_script()
        self.fragmentation_set = create_lcms_fragmentation_set()
        self.annotationquery = AnnotationQuery.objects.get_or_create(
            name='TestQuery',
            fragmentation_set=self.fragmentation_set,
            annotation_tool=AnnotationTool.objects.get(name='MassBank'),
        )[0]
        self.mass_bank_tool = MassBankQueryTool(self.annotationquery.id, self.fragmentation_set.id)


    def test_MassBankQueryTool_populate_annotations_table(self):

        """
        Due to the suspended batch service of MassBanK (from 17/08/15)
        it was decided that ensuring the populate annotations table
        method be unit tested was a priority as this could not be tested
        functionally.
        """

        # Set up false returned candidate annotations
        peak_set = Peak.objects.filter(fragmentation_set=self.fragmentation_set)
        peak_identifier = peak_set[0].slug
        annotation_results = [{
                'queryName': peak_identifier,
                'results': [{
                    'title': 'Catechin; LC-ESI-QTOF; MS2; CE:40 eV; [M-H]-',
                    'formula': 'C15H14O6',
                    'exactMass': 290.07904,
                    'score': 0.1896,
                    'id': 'PB002431',
                },
                    {
                        'title': '3alpha,7beta,12beta-Trihydroxy-5beta-cholan-24-oic acid; LC-ESI-TOF; MS; -60 V',
                        'formula': 'C24H40O5',
                        'exactMass': 408.28757,
                        'score': 0.0843,
                        'id': 'NU000207'
                    },
                    {
                        'title': 'Triclopyr; LC-ESI-QQ; MS2; CE:30 V; [M-H]-',
                        'formula': 'C7H4Cl3NO3',
                        'exactMass': 254.92568,
                        'score': 0.1641,
                        'id': 'WA000228'
                    }

                ],
                'numResults': 2,
        }]
        self.mass_bank_tool._populate_annotations_table(annotation_results)
        candidate_compound1 = Compound.objects.get(
            name='Catechin',
            formula='C15H14O6',
            exact_mass=290.07904
        )
        self.assertTrue(candidate_compound1, Compound)
        candidate_annotation  = CandidateAnnotation.objects.get(
            compound=candidate_compound1,
            confidence=0.1896,
            annotation_query=self.annotationquery,
            adduct='[M-H]-',
            instrument_type='LC-ESI-QTOF',
            collision_energy='40 eV'
        )
        self.assertTrue(candidate_annotation, CandidateAnnotation)


"""
When testing the models it was assumed the boiler-plate code of the django
framework was working correctly.
"""


class ExperimentModelTests(TestCase):
    """
    Test for Experiment model in Frank.models
    """

    def setUp(self):
        self.test_user = User.objects.create(
            username = 'testuser',
            password = 'testpass',
        )
        self.experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'LCMS DDA'
        )
        self.experiment = Experiment.objects.create(
            title='Experiment 1',
            description='This is a test experiment',
            created_by=self.test_user,
            ionisation_method=IONISATION_PROTOCOLS[0],
            detection_method=self.experimental_protocol,
        )


    def test_experiment_model_creation_valid_parameters(self):
        """
        Test to ensure experiment model created with valid parameters
        """
        self.assertTrue(isinstance(self.experiment, Experiment))


    def test_experiment_model_creation_invalid_parameters(self):
        """
        Test to ensure experiment model created with invalid parameters. These
        include all non-NULL fields (note: this is distinct from blank=False fields which
        are handled by the forms)
        """
        with self.assertRaises(ValueError):
            invalid_experiment = Experiment.objects.create(
                title='Experiment 1',
                description='This is a test experiment',
                # The creator of the experiment must be included
                created_by=None,
                ionisation_method=IONISATION_PROTOCOLS[0],
                detection_method=self.experimental_protocol,
            )

        with self.assertRaises(ValueError):
            invalid_experiment = Experiment.objects.create(
                title='Experiment 1',
                description='This is a test experiment',
                created_by=self.test_user,
                ionisation_method=IONISATION_PROTOCOLS[0],
                # The detection_method of the experiment must be included
                detection_method=None,
            )

    def test_experiment_save_method(self):
        """
        Test the save method updates the slug
        :return:
        """
        current_slug = self.experiment.slug
        # If the title of the experiment is updated, the slug should updated by save method
        self.experiment.title = 'Updated Experiment'
        self.experiment.save()
        self.assertTrue(self.experiment.slug==slugify(self.experiment.title))


    def test_experiment__unicode__(self):
        """
        Test to ensure the __unicode__(self) for experiment works as expected
        """
        self.assertTrue(self.experiment.__unicode__()=='Experiment '+str(self.experiment.id)+': '+self.experiment.title)


class UserExperimentsModelTests(TestCase):
    """
    Test for UserExperiment model in Frank.models
    """

    def setUp(self):
        self.test_user = User.objects.create(
            username = 'testuser',
            password = 'testpass',
        )
        self.experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'LCMS DDA'
        )
        self.experiment = Experiment.objects.create(
            title='Experiment 1',
            description='This is a test experiment',
            created_by=self.test_user,
            ionisation_method=IONISATION_PROTOCOLS[0],
            detection_method=self.experimental_protocol,
        )
        self.user_experiment = UserExperiment.objects.create(
            user=self.test_user,
            experiment=self.experiment,
        )


    def test_userexperiments_model_creation_valid_parameters(self):
        """
        Test to ensure UserExperiment model created with valid parameters
        """
        self.assertTrue(isinstance(self.user_experiment, UserExperiment))


    def test_userexperiment_model_creation_invalid_parameters(self):
        """
        Test to ensure UserExperiment model created with invalid parameters. These
        include all non-NULL fields
        """
        with self.assertRaises(ValueError):
            invalid_userexperiment = UserExperiment.objects.create(
                # A valid user is required
                user=None,
                experiment=self.experiment,
            )

        with self.assertRaises(ValueError):
            invalid_userexperiment = UserExperiment.objects.create(
                user=self.test_user,
                # A valid experiment is required
                experiment=None,
            )


    def test_experiment__unicode__(self):
        """
        Test to ensure the __unicode__(self) for UserExperiment works as expected
        """
        user_experiment = UserExperiment.objects.create(
            user=self.test_user,
            experiment=self.experiment,
        )
        self.assertTrue(self.user_experiment.__unicode__()==self.test_user.username+' access to '+self.experiment.title)


class ExperimentalConditionModelTests(TestCase):
    """
    Test for ExperimentalCondition model in Frank.models
    """

    def setUp(self):
        self.test_user = User.objects.create(
            username = 'testuser',
            password = 'testpass',
        )
        self.experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'LCMS DDA'
        )
        self.experiment = Experiment.objects.create(
            title='Experiment 1',
            description='This is a test experiment',
            created_by=self.test_user,
            ionisation_method=IONISATION_PROTOCOLS[0],
            detection_method=self.experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition',
            description = 'This is a test condition',
            experiment = self.experiment,
        )


    def test_experimental_condition_model_creation_valid_parameters(self):
        """
        Test to ensure ExperimentalCondition model created with valid parameters
        """
        self.assertTrue(isinstance(self.experimental_condition, ExperimentalCondition))


    def test_experimental_condition_model_creation_invalid_parameters(self):
        """
        Test to ensure ExperimentalCondition model created with invalid parameters. These
        include all non-NULL fields (note: this is distinct from blank=False fields which
        are handled by the forms)
        """
        with self.assertRaises(ValueError):
            invalid_experimental_condition = ExperimentalCondition.objects.create(
                name='Condition 1',
                description='This is a test condition',
                experiment=None,
            )


    def test_experimental_condition_save_method(self):
        """
        Test the save method updates the slug
        :return:
        """
        current_slug = self.experimental_condition.slug
        # If the title of the experimental condition is updated, the slug should updated by save method
        self.experimental_condition.name = 'Updated Condition'
        self.experimental_condition.save()
        self.assertTrue(self.experimental_condition.slug==slugify(self.experimental_condition.name))


    def test_experimental_condition__unicode__(self):
        """
        Test to ensure the __unicode__(self) for experimental condition works as expected
        """
        self.assertTrue(self.experimental_condition.__unicode__()==self.experimental_condition.name+' in '+self.experiment.title)


class SampleModelTests(TestCase):
    """
    Test for Sample model in Frank.models
    """

    def setUp(self):
        self.test_user = User.objects.create(
            username = 'testuser',
            password = 'testpass',
        )
        self.experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'LCMS DDA'
        )
        self.experiment = Experiment.objects.create(
            title='Experiment 1',
            description='This is a test experiment',
            created_by=self.test_user,
            ionisation_method=IONISATION_PROTOCOLS[0],
            detection_method=self.experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition',
            description = 'This is a test condition',
            experiment = self.experiment,
        )
        self.sample = Sample.objects.create(
            name = 'Test Sample',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'Human',
        )


    def test_sample_model_creation_valid_parameters(self):
        """
        Test to ensure ExperimentalCondition model created with valid parameters
        """
        self.assertTrue(isinstance(self.sample, Sample))


    def test_sample_model_creation_invalid_parameters(self):
        """
        Test to ensure Sample model created with invalid parameters. These
        include all non-NULL fields (note: this is distinct from blank=False fields which
        are handled by the forms)
        """
        with self.assertRaises(ValueError):
            invalid_experimental_condition = Sample.objects.create(
                name='Invalid Sample',
                description='This is an invalid test sample',
                experimental_condition=None,
                organism='Human',
            )


    def test_sample_save_method(self):
        """
        Test the save method updates the slug
        :return:
        """
        current_slug = self.sample.slug
        # If the name of the sample is updated, the slug should updated by save method
        self.sample.name = 'Updated Sample'
        self.sample.save()
        self.assertTrue(self.sample.slug==slugify(self.sample.name))


    def test_sample__unicode__(self):
        """
        Test to ensure the __unicode__(self) for sample works as expected
        """
        self.assertTrue(self.sample.__unicode__()=='Sample '+str(self.sample.id)+ ' in '+ self.experimental_condition.experiment.title)


class SampleFileModelTests(TestCase):
    """
    Test for SampleFile model in Frank.models
    """

    def setUp(self):
        self.test_user = User.objects.create(
            username = 'testuser',
            password = 'testpass',
        )
        self.experimental_protocol = ExperimentalProtocol.objects.create(
            name = 'LCMS DDA'
        )
        self.experiment = Experiment.objects.create(
            title='Experiment 1',
            description='This is a test experiment',
            created_by=self.test_user,
            ionisation_method=IONISATION_PROTOCOLS[0],
            detection_method=self.experimental_protocol,
        )
        self.experimental_condition = ExperimentalCondition.objects.create(
            name = 'Test Condition',
            description = 'This is a test condition',
            experiment = self.experiment,
        )
        self.sample = Sample.objects.create(
            name = 'Test Sample',
            description = 'This is a test sample',
            experimental_condition = self.experimental_condition,
            organism = 'Human',
        )
        self.sample_file = SampleFile.objects.create(
            name = 'TestSampleFile.mzXML',
            polarity = 'Negative',
            sample = self.sample,
        )


    def test_sample_file_model_creation_valid_parameters(self):
        """
        Test to ensure SampleFile model created with valid parameters
        """
        self.assertTrue(isinstance(self.sample_file, SampleFile))


    def test_sample_file_model_creation_invalid_parameters(self):
        """
        Test to ensure SampleFile model created with invalid parameters. These
        include all non-NULL fields (note: this is distinct from blank=False fields which
        are handled by the forms)
        """
        with self.assertRaises(ValueError):
            invalid_sample_file = SampleFile.objects.create(
                name='InvalidSampleFile.mzXML',
                polarity='Positive',
                # Sample field is a required field
                sample=None,
            )


    def test_sample__unicode__(self):
        """
        Test to ensure the __unicode__(self) for sample works as expected
        """
        self.assertTrue(self.sample_file.__unicode__()==self.sample_file.name)
