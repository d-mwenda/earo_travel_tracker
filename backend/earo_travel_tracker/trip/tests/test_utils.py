"""
Unittests for the Utils Mixin in the trip app.
"""
from django.test import TestCase, RequestFactory
from django.views.generic import TemplateView

from trip.utils import TripUtilsMixin
from trip.models import Trip
from traveler.models import TravelerProfile, Departments, Approver, CountrySecurityLevel
from django.contrib.auth import get_user_model


class TestUtilsMixin(TestCase):
    """
    TestCase for the Utils Mixin in the trip app.
    """

    class DummyView(TripUtilsMixin, TemplateView):
        """
        Basic view class to simulate typical use cases.
        """
        template_name = 'base.html'

    def setUp(self):
        # TODO
        # create department, country, approver
        # create 4 users: line manager, requester, department approvers,
        # country level approvers
        # Login user
        # create trip
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='testuser', password='12345')
        self.request = RequestFactory().get('/trip-view')
        self.view = self.DummyView()

    def test_user_owns_trip(self):
        """
        Test the user_owns_trip method.
        """
        # self.view.user_owns_trip()
        self.assertEqual('', '')
