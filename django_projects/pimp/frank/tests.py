from django.test import TestCase
from django.core.urlresolvers import reverse
from frank.models import *
from frank.forms import *
from django.contrib.auth.models import User
from pimp.
import unittest

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

    def test_experiment_creation(self):
        experiment = create_experiment()
        experiment.assertTrue(isinstance(experiment, Experiment))
