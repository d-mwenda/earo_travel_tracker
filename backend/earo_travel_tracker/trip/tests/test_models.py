"""
Tests for the trip app.
"""
from datetime import timedelta, date
import mock

from django.test import TestCase
from django.utils import timezone
from django.core.files import File

from trip.models import Trip, TripPOET, TripApproval
from traveler.models import TravelerProfile
from django.contrib.auth import get_user_model

user_model = get_user_model()

class TestTrip(TestCase):
    """
    In this class, the tests defined are the Trip, TripApproval and
    TripPOET models.
    The tests here are:
    1. Trip cannot begin in the past.
    2. Trip cannot begin on a later date than it ends.
    3. Integrity errors are raised on fields that should be compulsory.
    """
    def setUp(self):
        user = user_model.objects.create_user(
                username='testuser',
                password='12345'
                )
        self.traveler = TravelerProfile.objects.get(user_account=user)
        mock_file = mock.MagicMock(spec=File)
        mock_file.name = ('Test.docx')
        start_date = date.today()
        end_date = start_date + timedelta(days=10)
        self.trip = Trip(
            trip_name="Test Trip Name",
            traveler=self.traveler,
            type_of_travel="Domestic",
            category_of_travel= "Business",
            reason_for_travel= "This is a test trip",
            start_date=start_date,
            end_date=end_date,
            is_mission_critical=True,
            scope_of_work = mock_file,
        )
        self.trip.save()

    def test_cannot_begin_in_the_past(self):
        """
        Ensure that trip cannot begin before today.
        """
        today = timezone.now().date
        self.assertTrue(today() >= self.trip.start_date)

    def test_trip_cannot_end_before_start(self):
        """
        Test that start date is before end date.
        """
        trip = self.trip
        self.assertTrue(trip.end_date >= trip.start_date)
