from django.test import TestCase
from django.core.urlresolvers import reverse
from frank.models import *
from frank.forms import *
from frank.admin import *
from django.contrib.auth.models import User
from peakFactories import MSNPeakBuilder, GCMSPeakBuilder, PeakBuilder
import unittest
from django.template.defaultfilters import slugify
import rpy2.robjects as robjects
import rpy2.rlike.container as rlc
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django import forms
from django.contrib.admin.options import HORIZONTAL, VERTICAL, ModelAdmin, TabularInline
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError

# Test cases to ensure views work correctly

def create_user(username):
    username_user = User.objects.get_or_create(
        username = 'user_'+username,
        email = 'user_'+username+'@gmail.com',
        password = 'user'+username+'pass',
        first_name = username,
        last_name = username,
    )[0]
    return username_user

def create_experimental_protocol(experiment_protocol):
    test_experimental_protocol = ExperimentalProtocol.objects.get_or_create(
        name = experiment_protocol
    )[0]
    return test_experimental_protocol

def create_user_experiment(user, experiment):
    if user is None:
        user = create_user('experimentuser')
    if experiment is None:
        experiment = create_experiment('ExperimentUserTest')
    user_experiment = UserExperiments.objects.get_or_create(
        user = user,
        experiment = experiment,
    )[0]
    return user_experiment

def create_experiment(experiment_name):
    user = create_user('experiment')
    experimental_protocol = create_experimental_protocol('Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition')
    test_experiment = Experiment.objects.get_or_create(
        title = experiment_name,
        description = 'This is a test experiment',
        created_by = user,
        ionisation_method = 'EIS',
        detection_method = experimental_protocol,
    )[0]
    user_experiment = create_user_experiment(
        user = user,
        experiment = test_experiment,
    )
    return test_experiment

def create_fragmentation_set(name):
    fragmentation_set = FragmentationSet.objects.get_or_create(
        name = name,
        experiment = create_experiment(),
        status = 'Completed Successfully',
    )[0]
    return fragmentation_set

def create_sample_file(filename):
    sample_file = SampleFile.objects.get_or_create(
        name = filename,
        polarity = 'Positive',
        sample = create_sample(),
    )[0]
    return sample_file

def create_sample(name):
    sample = Sample.objects.get_or_create(
        name = name,
        description = 'Test description',
        experimental_condition = create_experimental_condition('sample_test'),
        organism = '',
    )[0]
    return sample

def create_experimental_condition(name):
    experimental_condition = ExperimentalCondition.objects.get_or_create(
        name = name,
        description = '',
        experiment = create_experiment(),
    )[0]
    return experimental_condition

def create_a_peak(sample_file, level, frag_set, parent_peak):
    if fragmentation_set == None:
        fragmentation_set = create_fragmentation_set('testfragset')
    peak = Peak.objects.get_or_create(
        source_file = create_sample_file(sample_file),
        mass = 100,
        retention_time = 125,
        intensity = 4000,
        parent_peak = None,
        msn_level = level,
        fragmentation_set = create_fragmentation_set(),
    )[0]
    return peak



class ExperimentModelTests(TestCase):

    def setUp(self):
        self.experiment = create_experiment('test experiment 1')

    # Test that experiment model instances can be created with correct input data
    def test_experiment_valid_creation(self):
        self.assertTrue(isinstance(self.experiment, Experiment))

    # Test that experiment model instances cannot be created with invalid params
    def test_experiment_invalid_parameters(self):
        with self.assertRaises(Exception):
            Experiment.objects.get_or_create(
                title = '',
                description = '',
                created_by = None,
                ionisation_method = 'Something Invalid',
                detection_method = 'Something else invalid',
            )[0]

    # Ensure updating the overridden save method does not alter the slug
    def test_experiment_save(self):
        title = 'Test Experiment 1'
        experiment = Experiment(
            title = title,
            description = 'This is a test experiment',
            created_by = create_user('testuser'),
            ionisation_method = 'EIS',
            detection_method = create_experimental_protocol('Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'),
        )
        proposed_id = Experiment.objects.count()+1
        intended_slug = slugify(title+'-'+str(proposed_id))
        experiment.save()
        self.assertTrue(experiment.slug == intended_slug)
        ## Update the model and ensure that the slug field is not altered
        experiment.title('Test Experiment 2.')
        experiment.save()
        self.assertTrue(experiment.slug == intended_slug)
    #
    # # Ensure the __unicode__(self) method is correct
    # def test_experiment__unicode__(self):
    #     experiment = create_experiment()
    #     experiment_id = experiment.id
    #     experiment_title = experiment.title
    #     proposed_unicode = 'Experiment '+str(experiment_id)+': '+experiment_title
    #     self.assertTrue(experiment.__unicode__==proposed_unicode)

# class UserExperimentModelTests(TestCase):
#
#     # Test that experiment model instances can be created with correct input data
#     def test_user_experiments_creation(self):
#         new_user = create_user()
#         experiment = create_experiment()
#         user_experiment = create_user_experiment(new_user, experiment)
#         user_experiment.assertTrue(isinstance(user_experiment, UserExperiment))
#
#     # Test that user_experiments cannot be created with either an invalid user or experiment
#
#         # Ensure the __unicode__(self) method is correct
#     # def test_experiment__unicode__(self):
#     #     experiment = create_experiment()
#     #     experiment_id = experiment.id
#     #     experiment_title = experiment.title
#     #     proposed_unicode = 'Experiment '+str(experiment_id)+': '+experiment_title
#     #     self.assertTrue(experiment.__unicode__==proposed_unicode)
#
# class ExperimentalConditionModelTests(TestCase):
#
#     def test_experimental_condition_creation(self):
#         pass
#
#     # Test that an Experimental Condition cannot be created with invalid params
#
#     # Test that the overridden save method will not alter the slug field
#
#     # Test that the __unicode__ method works correctly
#
# class SampleModelTests(Testcase):
#
#     def test_sample_creation(self):
#         pass
#
#     # Test that a sample cannot be created with invalid params
#
#     # Test the overridden save method
#
#     # Test the __unicode__ method returns the correct description
#
# class FragmentationSetModelTests(TestCase):
#
#     # Test that instances of the fragmentation set can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test that the overridden save method and won't change the slug
#
#      # Test the __unicode__ method returns the correct description
#
# class AnnotationQueryModelTest(TestCase):
#
#     # Test that instances of the annotation query can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test that the overridden save method and won't change the slug
#
#      # Test the __unicode__ method returns the correct description
#
# class AnnotationToolModelTest(TestCase):
#
#     # Test that instances of the annotation tool can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test that the overridden save method and won't change the slug
#
#      # Test the __unicode__ method returns the correct description
#
# class CompoundModelTest(TestCase):
#
#     # Test that instances of compound model can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test that the overridden save method and won't change the slug
#
#     # Test the __unicode__ method returns the correct description
#
# class PeakModelTest(TestCase):
#
#     # Test that instances of peak model can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test that the overridden save method and won't change the slug
#
#     # Test the __unicode__ method returns the correct description
#
# class CandidateAnnotationModelTest(TestCase):
#
#     # Test that instances of candidate annotation model can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test the __unicode__ method returns the correct description
#
# class ExperimentalProtocolModelTest(TestCase):
#
#     # Test that instances of experimental protocol model can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test the __unicode__ method returns the correct description
#
# class AnnotationToolProtocolsModelTest(TestCase):
#
#     # Test that instances of annotation tool protocol model can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test the __unicode__ method returns the correct description
#
# class AnnotationQueryHierarchyModelTest(TestCase):
#
#     # Test that instances of annotation tool protocol model can be created
#
#     # Test that invalid parameters throw and exception
#
#     # Test the __unicode__ method returns the correct description
#
# class GetUploadFileNameTest(TestCase):
#
#     # Test that the filepath returned for a new file is as anticipated - file exists
#
#     # Test that the directory is created in the event that it did not previously exist
#
#     # Test that the name of the filepath is unique, and does not save over an existing file
#
# class ExperimentModelTests(TestCase):
#
#     # Test that experiment model instances can be created with correct input data
#     def test_experiment_creation(self):
#         experiment = create_experiment()
#         self.assertTrue(isinstance(experiment, Experiment))
#
#     # Test that experiment model instances cannot be created with invalid params
#
#     # Ensure updating the overridden save method does not alter the slug
#     def test_experiment_save(self):
#         title = 'Test Experiment 1'
#         experiment = Experiment(
#             title = title,
#             description = 'This is a test experiment',
#             created_by = create_user(),
#             ionisation_method = 'EIS',
#             detection_method = create_experimental_protocol(),
#         )
#         proposed_id = Experiment.objects.count()+1
#         intended_slug = slugify(title+'-'+str(proposed_id))
#         experiment.save()
#         self.assertTrue(experiment.slug == intended_slug)
#         ## Update the model and ensure that the slug field is not altered
#         experiment.description('This is now a new test description.')
#         experiment.save()
#         self.assertTrue(experiment.slug == intended_slug)
#
#     # Ensure the __unicode__(self) method is correct
#     def test_experiment__unicode__(self):
#         experiment = create_experiment()
#         experiment_id = experiment.id
#         experiment_title = experiment.title
#         proposed_unicode = 'Experiment '+str(experiment_id)+': '+experiment_title
#         self.assertTrue(experiment.__unicode__==proposed_unicode)
#
#
# class PeakBuilderTests(TestCase):
#
#     def test_peakBuilder_creation_throws_exception(self):
#         """
#         Test to ensure abstract class "PeakBuilder" cannot be instantiated
#         """
#         self.assertRaises(TypeError, PeakBuilder)
#
# class MSNPeakBuilderTests(TestCase):
#
#
#     def setUp(self):
#         """
#         Set up of testing parameters
#         """
#         self.fragmentation_set = create_fragmentation_set()
#         self.sample_file = create_sample_file(),
#         string_factor_filenames = robjects.StrVector((
#             "file1.mzXML", "file1.mzXML", "file1.mzXML", "file1.mzXML", "file1.mzXML","file1.mzXML"
#         ))
#         factor_vector_filenames = string_factor_filenames.factor()
#         peak_ID_vector = robjects.IntVector((1, 2, 3, 4, 5, 6))
#         msn_parent_peak_ID_vector = robjects.IntVector((0, 1, 1, 1, 2, 0))
#         ms_level_vector = robjects.IntVector((1, 2, 2, 2, 3, 1))
#         rt_vector = robjects.FloatVector((100.1, 100.1, 100.1, 100.1, 100.1, 127.7))
#         mz_vector = robjects.FloatVector((222.2, 101.1, 78.9, 65.5, 50.0, 280.1))
#         intensity_vector = robjects.FloatVector((2220.2, 1010.1, 780.9, 650.5, 200.1, 2100.1))
#         sample_vector = robjects.IntVector((1, 1, 1, 1, 1, 1))
#         group_peak_vector = robjects.IntVector((0, 0, 0, 0, 0, 0))
#         collision_energy_vector = robjects.IntVector((1, 1, 1, 1, 1, 1))
#         valid_data = rlc.OrdDict([
#             ('peakID', peak_ID_vector),
#             ('MSnParentPeakID', msn_parent_peak_ID_vector),
#             ('msLevel', ms_level_vector),
#             ('rt', rt_vector),
#             ('mz', mz_vector),
#             ('intensity', intensity_vector),
#             ('Sample', sample_vector),
#             ('GroupPeakMSN', group_peak_vector),
#             ('CollisionEnergy', collision_energy_vector),
#             ('SourceFile', factor_vector_filenames),
#         ])
#         self.valid_r_dataframe_input = robjects.DataFrame(valid_data)
#         self.valid_fragmentation_set_id_input = self.fragmentation_set.id
#         self.invalid_type_r_dataframe_input = ""
#         self.invalid_type_fragmentation_set_id_input = ""
#         self.invalid_type_r_dataframe_input = ""
#         self.invalid_type_fragmentation_set_id_input = ""
#         self.invalid_value_fragmentation_set_id_input = -1
#
#
#     def test_MSNPeakBuilder_init_invalid_parameter_types_supplied(self):
#         """
#         Test that MSNPeakBuilder cannot be instantiated with invalid types of parameters
#         """
#         # Check with no given parameters
#         with self.assertRaises(TypeError):
#             MSNPeakBuilder()
#         # Check with None parameters given
#         with self.assertRaises(TypeError):
#             MSNPeakBuilder(None, None)
#         # Check with invalid type for fragmentation_set_id
#         with self.assertRaises(TypeError):
#             MSNPeakBuilder(self.valid_r_dataframe_input, self.invalid_type_fragmentation_set_id_input)
#         # Check with invalid type for parameter r_dataframe
#         with self.assertRaises(TypeError):
#             MSNPeakBuilder(self.invalid_type_r_dataframe_input, self.valid_fragmentation_set_id_input)
#         # Check with invalid types for both the r_dataframe and fragmentation_set_id types
#         with self.assertRaises(TypeError):
#             MSNPeakBuilder(self.invalid_type_r_dataframe_input, self.invalid_type_fragmentation_set_id_input)
#         # Check to ensure the fragmentation_set_id given corresponds to an existing fragmentation set
#         with self.assertRaises(ValueError):
#             MSNPeakBuilder(self.valid_r_dataframe_input, self.invalid_value_fragmentation_set_id_input)
#
#
#     def test_MSNPeakBuilder_init_valid_parameters_supplied(self):
#         """
#         Test that MSNPeakBuilder can be instantiated with valid parameters
#         """
#         self.assertTrue(isinstance(MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input), MSNPeakBuilder))
#
#
#     def test_createAPeak_valid_parameters(self):
#         """
#         Test that createAPeak creates new Peak model instance when passed valid parameters
#         """
#         peak_array_index = 2
#         parent_peak_object = create_a_peak()
#         peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
#         self.assertTrue(isinstance(peak_builder_object._createAPeak(peak_array_index, parent_peak_object), Peak))
#
#
#     def test_getParentPeak(self):
#         """
#         Test that getParentPeak returns the precursor peak of a given fragment
#         """
#         peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
#         parent_id_from_r = 2
#         # Ensure the parent peak is created
#         parent_peak = peak_builder_object._getParentPeak(parent_id_from_r)
#         self.assertTrue(isinstance(parent_peak, Peak))
#         # Also check that the parent peak's precursor was created
#         self.assertTrue(isinstance(parent_peak.parent_peak, Peak))
#
#
#     def test_populate_database_peaks(self):
#         """
#         Test to ensure that populate_database_peaks does not throw any errors
#         """
#         peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
#         peak_builder_object.populate_database_peaks()
#         peak_query_set = Peak.objects.filter(fragmentation_set = self.fragmentation_set)
#         ## Check all test peaks with fragments have been created - using test data m/z to identify them
#         self.assertTrue(isinstance(peak_query_set.get(mass=222.2), Peak))
#         self.assertTrue(isinstance(peak_query_set.get(mass=101.1), Peak))
#         self.assertTrue(isinstance(peak_query_set.get(mass=78.9), Peak))
#         self.assertTrue(isinstance(peak_query_set.get(mass=65.5), Peak))
#         self.assertTrue(isinstance(peak_query_set.get(mass=50.0), Peak))
#         ## The final test peak should not be created as it has no associated fragments or parent ion, therefore is of no interest
#         with self.assertRaises(ObjectDoesNotExist):
#             peak_query_set.get(mass=280.1)
#
#
# class MSNPeakBuilderTests(TestCase):
#
#     def setUp(self):
#         pass
#
#     def test_GCMSPeakBuilder_init_valid_parameters(self):
#         pass
#
#     def test_GCMSPeakBuilder_init_invalid_parameters(self):
#         pass
#
#     def test_GCMSPeakBuilder_init_invalid_parameters(self):
#         pass

#################### MODEL TESTS ###################

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