"""
This script defines tests for the views implementation
"""
from django import test
from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

user_model = get_user_model()


class BaseViewTestCase(test.TestCase):
    """
    Implement common methods shared across view test cases.
    TODO: this can be shared accross apps.
    """
    def setUp(self):
        self.client = Client()
        Group.objects.create(name="travelers")
        self.user = user_model.objects.create(username="derick", password="mwenda")
        self.client.post("/login/", {"username": "derick", "password": "mwenda"})

    def tearDown(self):
        self.client.get("logout")


class TestTripCRUDView(BaseViewTestCase):
    """
    Tests for the Trip Create View.
    The implemented tests are:
    1. Test that user needs permission
    """

    def test_get_create(self):
        """
        test get method on the TripCreateView returns http OK.
        """
        response = self.client.get("/trip/new-trip", follow=True)
        print(response.redirect_chain)
        self.assertEqual(response.status_code, 200)
    
    def test_post_create(self):
        """
        test post method on the TripCreateView returns Http 201
        """
        response = self.client.post("/trip/new-trip", {
            "trip_name": "Test trip",
            })
        self.assertEqual(response.status_code, 201)

    def test_get_detail(self):
        """
        Test get method on the TripDetailView returns http OK.
        """
        response = self.client.get("trip-details/trip=1")
        self.assertEqual(response.status_code, 200)
        # TODO assert context variables are as expected

    def test_post_detail(self):
        """
        Test get method on the TripDetailView returns http OK.
        """
        response = self.client.post("trip-details/trip=1", {"": ""})
        self.assertEqual(response.status_code, 201)
        # TODO assert context variables are as expected
        # self.assert(response.context[""]
