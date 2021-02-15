"""
This script defines tests for the views implementation
"""
from django import test
from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

user_model = get_user_model()


class TestTripCreateView(test.TestCase):
    """
    Tests for the Trip Create View.
    The implemented tests are:
    1. Test that user needs permission
    """
    def setUp(self):
        self.client = Client()
        Group.objects.create(name="travelers")
        self.user = user_model.objects.create(username="derick", password="mwenda")
        self.client.post('/login/', {"username": "derick", "password": "mwenda"})

    def test_get(self):
        """
        test get method on the returns http OK.
        """
        self

    def tearDown(self):
        self.client.get('logout')
