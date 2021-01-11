"""
Tests for the trip app.
"""
from django.test import TestCase
from django.utils import timezone

from .models import Trips


# Todo test that new trips are unapproved by default and modifications to a trip instance do affect approval.
class TestTripsModel(TestCase):
    """
    The tests here are:
    1. Trip cannot begin in the past.
    2. Trip cannot begin on a later date than it ends.
    3. Integrity errors are raised on fields that should be compulsory.
    """
    def setUp(self):
        self.trip = Trips()
        self.trip.save()

    def test_cannot_begin_in_the_past(self):
        """
        Ensure that trip cannot begin before today.
        """
        today = timezone.now().date
        self.assertTrue(today > self.trip.start_date)

    def test_trip_cannot_end_before_start(self):
        """
        Test that start date is before end date.
        """
        trip = Trips()
        self.assertTrue(trip.end_date > trip.start_date)
