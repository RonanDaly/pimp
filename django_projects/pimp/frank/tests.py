from django.test import TestCase
from django.core.urlresolvers import reverse
from frank.models import *
from frank.forms import *
from django.contrib.auth.models import User
from pimp.
import unittest
from django.template.defaultfilters import slugify

# Create your tests here.

# Test cases to ensure views work correctly

def create_user():
    test_user = User.objects.create(
        username = 'testuser',
        email = 'scottgreig27@gmail.com',
        password = 'testpass',
        first_name = 'Test',
        last_name = 'User',
    )
    return test_user

def create_experimental_protocol():
    test_experimental_protocol = ExperimentalProtocol.objects.create(
        name = 'Test Experimental Protocol'
    )
    return test_experimental_protocol

def create_user_experiment(user, experiment):
    if user is None:
        user = create_user()
    if experiment is None:
        experiment = create_experiment()
    user_experiment = UserExperiment.objects.create(
        user = user,
        experiment = experiment,
    )
    return user_experiment

def create_experiment():
    user = create_user()
    experimental_protocol = create_experimental_protocol()
    test_experiment = Experiment.objects.create(
        title = 'Test Experiment 1',
        description = 'This is a test experiment',
        created_by = create_user(),
        ionisation_method = 'EIS',
        detection_method = create_experimental_protocol(),
    )
    user_experiment = create_user_experiment(
        user = user,
        experiment = test_experiment,
    )
    return test_experiment


class ExperimentModelTests(TestCase):

    # Test that experiment model instances can be created with correct input data
    def test_experiment_creation(self):
        experiment = create_experiment()
        self.assertTrue(isinstance(experiment, Experiment))

    # Test that experiment model instances cannot be created with invalid params

    # Ensure updating the overridden save method does not alter the slug
    def test_experiment_save(self):
        title = 'Test Experiment 1'
        experiment = Experiment(
            title = title,
            description = 'This is a test experiment',
            created_by = create_user(),
            ionisation_method = 'EIS',
            detection_method = create_experimental_protocol(),
        )
        proposed_id = Experiment.objects.count()+1
        intended_slug = slugify(title+'-'+str(proposed_id))
        experiment.save()
        self.assertTrue(experiment.slug == intended_slug)
        ## Update the model and ensure that the slug field is not altered
        experiment.description('This is now a new test description.')
        experiment.save()
        self.assertTrue(experiment.slug == intended_slug)

    # Ensure the __unicode__(self) method is correct
    def test_experiment__unicode__(self):
        experiment = create_experiment()
        experiment_id = experiment.id
        experiment_title = experiment.title
        proposed_unicode = 'Experiment '+str(experiment_id)+': '+experiment_title
        self.assertTrue(experiment.__unicode__==proposed_unicode)

class UserExperimentModelTests(TestCase):

    # Test that experiment model instances can be created with correct input data
    def test_user_experiments_creation(self):
        new_user = create_user()
        experiment = create_experiment()
        user_experiment = create_user_experiment(new_user, experiment)
        user_experiment.assertTrue(isinstance(user_experiment, UserExperiment))

    # Test that user_experiments cannot be created with either an invalid user or experiment

        # Ensure the __unicode__(self) method is correct
    # def test_experiment__unicode__(self):
    #     experiment = create_experiment()
    #     experiment_id = experiment.id
    #     experiment_title = experiment.title
    #     proposed_unicode = 'Experiment '+str(experiment_id)+': '+experiment_title
    #     self.assertTrue(experiment.__unicode__==proposed_unicode)

class ExperimentalConditionModelTests(TestCase):

    def test_experimental_condition_creation(self):
        pass

    # Test that an Experimental Condition cannot be created with invalid params

    # Test that the overridden save method will not alter the slug field

    # Test that the __unicode__ method works correctly

class SampleModelTests(Testcase):

    def test_sample_creation(self):
        pass

    # Test that a sample cannot be created with invalid params

    # Test the overridden save method

    # Test the __unicode__ method returns the correct description

class FragmentationSetModelTests(TestCase):

    # Test that instances of the fragmentation set can be created

    # Test that invalid parameters throw and exception

    # Test that the overridden save method and won't change the slug

     # Test the __unicode__ method returns the correct description

class AnnotationQueryModelTest(TestCase):

    # Test that instances of the annotation query can be created

    # Test that invalid parameters throw and exception

    # Test that the overridden save method and won't change the slug

     # Test the __unicode__ method returns the correct description

class AnnotationToolModelTest(TestCase):

    # Test that instances of the annotation tool can be created

    # Test that invalid parameters throw and exception

    # Test that the overridden save method and won't change the slug

     # Test the __unicode__ method returns the correct description

class CompoundModelTest(TestCase):

    # Test that instances of compound model can be created

    # Test that invalid parameters throw and exception

    # Test that the overridden save method and won't change the slug

    # Test the __unicode__ method returns the correct description

class PeakModelTest(TestCase):

    # Test that instances of peak model can be created

    # Test that invalid parameters throw and exception

    # Test that the overridden save method and won't change the slug

    # Test the __unicode__ method returns the correct description

class CandidateAnnotationModelTest(TestCase):

    # Test that instances of candidate annotation model can be created

    # Test that invalid parameters throw and exception

    # Test the __unicode__ method returns the correct description

class ExperimentalProtocolModelTest(TestCase):

    # Test that instances of experimental protocol model can be created

    # Test that invalid parameters throw and exception

    # Test the __unicode__ method returns the correct description

class AnnotationToolProtocolsModelTest(TestCase):

    # Test that instances of annotation tool protocol model can be created

    # Test that invalid parameters throw and exception

    # Test the __unicode__ method returns the correct description

class AnnotationQueryHierarchyModelTest(TestCase):

    # Test that instances of annotation tool protocol model can be created

    # Test that invalid parameters throw and exception

    # Test the __unicode__ method returns the correct description

class GetUploadFileNameTest(TestCase):

    # Test that the filepath returned for a new file is as anticipated - file exists

    # Test that the directory is created in the event that it did not previously exist

    # Test that the name of the filepath is unique, and does not save over an existing file


