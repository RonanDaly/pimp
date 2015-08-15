from django.test import TestCase
from django.core.urlresolvers import reverse
from frank.models import *
from frank.forms import *
from django.contrib.auth.models import User
from peakFactories import MSNPeakBuilder, GCMSPeakBuilder, PeakBuilder
import unittest
from django.template.defaultfilters import slugify
from argparse import ArgumentError
import rpy2.robjects as robjects
import rpy2.rlike.container as rlc
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# Create your tests here.

# Test cases to ensure views work correctly

def create_user():
    test_user = User.objects.get_or_create(
        username = 'testuser',
        email = 'testuser@gmail.com',
        password = 'testpass',
        first_name = 'Test',
        last_name = 'User',
    )[0]
    return test_user

def create_experimental_protocol():
    test_experimental_protocol = ExperimentalProtocol.objects.get_or_create(
        name = 'Test Experimental Protocol'
    )[0]
    return test_experimental_protocol

def create_user_experiment(user, experiment):
    if user is None:
        user = create_user()
    if experiment is None:
        experiment = create_experiment()
    user_experiment = UserExperiments.objects.get_or_create(
        user = user,
        experiment = experiment,
    )[0]
    return user_experiment

def create_experiment():
    user = create_user()
    experimental_protocol = create_experimental_protocol()
    test_experiment = Experiment.objects.get_or_create(
        title = 'Test Experiment 1',
        description = 'This is a test experiment',
        created_by = create_user(),
        ionisation_method = 'EIS',
        detection_method = create_experimental_protocol(),
    )[0]
    user_experiment = create_user_experiment(
        user = user,
        experiment = test_experiment,
    )
    return test_experiment

def create_fragmentation_set():
    fragmentation_set = FragmentationSet.objects.get_or_create(
        name = "TestFragmentationSet",
        experiment = create_experiment(),
        status = 'Completed Successfully',
    )[0]
    return fragmentation_set

def create_sample_file():
    sample_file = SampleFile.objects.get_or_create(
        name = 'file1.mzXML',
        polarity = 'Positive',
        sample = create_sample(),
    )[0]
    return sample_file

def create_sample():
    sample = Sample.objects.get_or_create(
        name = 'TestSample',
        description = '',
        experimental_condition = create_experimental_condition(),
        organism = '',
    )[0]
    return sample

def create_experimental_condition():
    experimental_condition = ExperimentalCondition.objects.get_or_create(
        name = 'TestCondition',
        description = '',
        experiment = create_experiment(),
    )[0]
    return experimental_condition

def create_a_peak():
    peak = Peak.objects.get_or_create(
        source_file = create_sample_file(),
        mass = 100,
        retention_time = 125,
        intensity = 4000,
        parent_peak = None,
        msn_level = 1,
        fragmentation_set = create_fragmentation_set(),
    )[0]
    return peak

#
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


class PeakBuilderTests(TestCase):

    def test_peakBuilder_creation_throws_exception(self):
        """
        Test to ensure abstract class "PeakBuilder" cannot be instantiated
        """
        self.assertRaises(TypeError, PeakBuilder)

class MSNPeakBuilderTests(TestCase):


    def setUp(self):
        """
        Set up of testing parameters
        """
        self.fragmentation_set = create_fragmentation_set()
        self.sample_file = create_sample_file(),
        string_factor_filenames = robjects.StrVector((
            "file1.mzXML", "file1.mzXML", "file1.mzXML", "file1.mzXML", "file1.mzXML","file1.mzXML"
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
        self.invalid_type_r_dataframe_input = ""
        self.invalid_type_fragmentation_set_id_input = ""
        self.invalid_type_r_dataframe_input = ""
        self.invalid_type_fragmentation_set_id_input = ""
        self.invalid_value_fragmentation_set_id_input = -1


    def test_MSNPeakBuilder_init_invalid_parameter_types_supplied(self):
        """
        Test that MSNPeakBuilder cannot be instantiated with invalid types of parameters
        """
        # Check with no given parameters
        with self.assertRaises(TypeError):
            MSNPeakBuilder()
        # Check with None parameters given
        with self.assertRaises(TypeError):
            MSNPeakBuilder(None, None)
        # Check with invalid type for fragmentation_set_id
        with self.assertRaises(TypeError):
            MSNPeakBuilder(self.valid_r_dataframe_input, self.invalid_type_fragmentation_set_id_input)
        # Check with invalid type for parameter r_dataframe
        with self.assertRaises(TypeError):
            MSNPeakBuilder(self.invalid_type_r_dataframe_input, self.valid_fragmentation_set_id_input)
        # Check with invalid types for both the r_dataframe and fragmentation_set_id types
        with self.assertRaises(TypeError):
            MSNPeakBuilder(self.invalid_type_r_dataframe_input, self.invalid_type_fragmentation_set_id_input)
        # Check to ensure the fragmentation_set_id given corresponds to an existing fragmentation set
        with self.assertRaises(ValueError):
            MSNPeakBuilder(self.valid_r_dataframe_input, self.invalid_value_fragmentation_set_id_input)


    def test_MSNPeakBuilder_init_valid_parameters_supplied(self):
        """
        Test that MSNPeakBuilder can be instantiated with valid parameters
        """
        self.assertTrue(isinstance(MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input), MSNPeakBuilder))


    def test_createAPeak_valid_parameters(self):
        """
        Test that createAPeak creates new Peak model instance when passed valid parameters
        """
        peak_array_index = 2
        parent_peak_object = create_a_peak()
        peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
        self.assertTrue(isinstance(peak_builder_object._createAPeak(peak_array_index, parent_peak_object), Peak))


    def test_getParentPeak(self):
        """
        Test that getParentPeak returns the precursor peak of a given fragment
        """
        peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
        parent_id_from_r = 2
        # Ensure the parent peak is created
        parent_peak = peak_builder_object._getParentPeak(parent_id_from_r)
        self.assertTrue(isinstance(parent_peak, Peak))
        # Also check that the parent peak's precursor was created
        self.assertTrue(isinstance(parent_peak.parent_peak, Peak))


    def test_populate_database_peaks(self):
        """
        Test to ensure that populate_database_peaks does not throw any errors
        """
        peak_builder_object = MSNPeakBuilder(self.valid_r_dataframe_input, self.valid_fragmentation_set_id_input)
        peak_builder_object.populate_database_peaks()
        peak_query_set = Peak.objects.filter(fragmentation_set = self.fragmentation_set)
        ## Check all test peaks with fragments have been created - using test data m/z to identify them
        self.assertTrue(isinstance(peak_query_set.get(mass=222.2), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=101.1), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=78.9), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=65.5), Peak))
        self.assertTrue(isinstance(peak_query_set.get(mass=50.0), Peak))
        ## The final test peak should not be created as it has no associated fragments or parent ion, therefore is of no interest
        with self.assertRaises(ObjectDoesNotExist):
            peak_query_set.get(mass=280.1)


class MSNPeakBuilderTests(TestCase):

    def setUp(self):
        pass

    def test_GCMSPeakBuilder_init_valid_parameters(self):
        pass

    def test_GCMSPeakBuilder_init_invalid_parameters(self):
        pass

    def test_GCMSPeakBuilder_init_invalid_parameters(self):
        pass

