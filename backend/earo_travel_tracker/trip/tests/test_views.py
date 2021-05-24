"""
This script defines tests for the views implementation
"""
from django import test
from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import resolve

from guardian.shortcuts import assign_perm

from trip.models import Trip, TripItinerary, TripPOET
from traveler.models import Departments, CountrySecurityLevel

user_model = get_user_model()


def prepare_travelers_group():
    """
    Check the travelers group exists or create one for
    the associated signal to fire correctly.
    """
    if not Group.objects.filter(name="travelers").exists():   
        travelers = Group.objects.create(name="travelers")
        # assign perms
        perms = [
            (Trip, "add_trip"),
            (CountrySecurityLevel, "view_countrysecuritylevel"),
            (TripItinerary, "add_tripitinerary"),
            (TripPOET, "add_trippoet"),
            (Departments, "view_departments"),
        ]
        for perm in perms:
            content_type = ContentType.objects.get_for_model(perm[0])
            permission = Permission.objects.get(
                codename=perm[1],
                content_type=content_type
            )
            travelers.permissions.add(permission)


class TestAuthentication(test.TestCase):
    """
    Test that the user can login.
    """
    def setUp(self):
        """
        Prepare the pre-requisites.
        """
        prepare_travelers_group()
        self.user = user_model.objects.create_user(username="login_tester", password="can_login")

    def test_login(self):
        """
        Test that users can log in.
        """
        logged_in = self.client.login(username="login_tester", password="can_login")
        self.assertTrue(logged_in, "User wasn't logged in.")


class BaseViewTestCase(test.TestCase):
    """
    Implement common methods shared across view test cases.
    TODO: this can be shared accross apps.
    """
    def setUp(self):
        prepare_travelers_group()
        self.client = Client()
        self.user = user_model.objects.create_user(username="derick", password="mwenda")
        self.client.force_login(self.user)


class TestTripCRUDView(BaseViewTestCase):
    """
    Tests for the Trip Create View.
    The implemented tests are:
    1. Test that user needs permission
    """

    def test_url_conf(self):
        """
        Test that the URLs are resolve as expected.
        """
        resolved_to = resolve("/trip/new-trip")
        self.assertEqual(resolved_to.func.__name__, "TripCreateView")
        self.assertEqual(resolved_to.view_name, "u_create_trip")

    def test_get_create(self):
        """
        test get method on the TripCreateView returns http OK.
        """
        response = self.client.get("/trip/new-trip", follow=True)
        self.assertEqual(response.status_code, 200)

    # def test_post_create(self):
    #     """
    #     test post method on the TripCreateView returns Http 201
    #     """
        # Test errors in dates when end date greater than start and start in the past
    #     response = self.client.post("/trip/new-trip", {
    #         "trip_name": "Test trip",
    #         })
    #     self.assertEqual(response.status_code, 201)

    # def test_get_detail(self):
    #     """
    #     Test get method on the TripDetailView returns http OK.
    #     """
    #     response = self.client.get("trip-details/trip=1")
    #     self.assertEqual(response.status_code, 200)
        # TODO assert context variables are as expected

    # def test_post_detail(self):
    #     """
    #     Test get method on the TripDetailView returns http OK.
    #     """
    #     response = self.client.post("trip-details/trip=1", {"trip_id": 1})
    #     self.assertEqual(response.status_code, 201)
        # TODO assert context variables are as expected
        # self.assert(response.context[""]
