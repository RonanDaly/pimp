from django.test import TestCase, Client
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


#################### VIEWS TESTS ###################


"""
As the existing application does not use the default Django authentication,
client.login() does not work so a default authenticated client must first be
made.
"""


class IndexTestView(TestCase):
    """
    Tests for the index page of frank.views
    """

    def setUp(self):
        username = 'testuser2'
        email = 'test@gmail.com'
        password = 'password'
        test_user= User.objects.create(
            username=username,
            email=email,
            password=password,
        )
        self.authenticated_client = self.client
        response = self.authenticated_client.post('/accounts/login/', {'username': username, 'password': password})


    def test_index_with_authenticated_client(self):
        response = self.authenticated_client.get(reverse('frank_index'))
        self.assertTrue(response.status_code, 200)


    def test_index_with_non_authenticated_client(self):
        response = self.client.get(reverse('frank_index'))
        self.assertRedirects(response, 'accounts/login/?next=/frank/')


class MyExperimentsViewTest(TestCase):
    """
    Test for the my_experiments view in frank.views
    """

    def setUp(self):
        username = 'testuser2'
        email = 'test@gmail.com'
        password = 'password'
        test_user= User.objects.create(
            username=username,
            email=email,
            password=password,
        )
        self.authenticated_client = self.client
        response = self.authenticated_client.post('/accounts/login/', {'username': username, 'password': password})


    def test_my_experiment_view_renders_for_authenticated_user(self):
        response = self.authenticated_client.get(reverse('my_experiments'))
        self.assertRedirects(response, 'accounts/login/?next=/frank/my_experiments')
        self.assertEquals(response.status_code, 200)
