"""
Data models for the trip app are defined in this file.
"""
from django.db import models
from django.conf import settings
# earo_travel_tracker imports
from traveler.models import TravelerDetails


class Trips(models.Model):
    """
    This class implements the data model for all trips taken.
    """
    # TODO Implement a method to create a new approval instance whenever every trip is created.
    TRAVEL_CATEGORIES = (
        ('Business', 'Business'),
        ('Home Leave', 'Home Leave'),
        ('R & R', 'R & R'),
        ('Personal', 'Personal'),
        ('Medical', 'Medical'),
        ('Compassionate', 'Compassionate'),
    )

    TRAVEL_TYPES = (
        ('Domestic', 'Domestic'),
        ('IntraContinental', 'IntraContinental'),
        ('International', 'International'),
    )

    TRAVEL_MODES = (
        ('Air', 'Air'),
        ('Land', 'Land'),
        ('Water', 'Water'),
    )

    traveler = models.ForeignKey(TravelerDetails, on_delete=models.CASCADE, null=False, blank=False)
    type_of_travel = models.CharField(max_length=15, null=False, blank=False, choices=TRAVEL_TYPES)
    categories_of_travel = models.CharField(max_length=15, null=False, blank=False,
                                            choices=TRAVEL_CATEGORIES)
    mode_of_travel = models.CharField(max_length=10, null=False, blank=False, choices=TRAVEL_MODES)
    reason_for_travel = models.CharField(max_length=1000, null=False, blank=False, help_text=
                                "Use less than 1000 characters to describe the reasons for travel")
    is_mission_critical = models.BooleanField(null=False, blank=False)
    is_travel_completed = models.BooleanField(null=False, blank=False, default=False)
    created_on = models.DateTimeField(auto_now=True, null=False)


class TripTravelerDependants(models.Model):
    """
    Dependants travelling with an employee are captured in this class.
    """
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE, null=False, blank=False)
    dependants_travelling = models.ForeignKey(TravelerDetails, on_delete=models.CASCADE,
                                                null=False, blank=False)


class TripExpenses(models.Model):
    """
    Trip expenses associated with a trip are capture by data models implemented in this class.
    """
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE, null=False, blank=False)
    type_of_expense = models.CharField(max_length=30, null=False, blank=False)
    currency = models.CharField(max_length=3, null=False, blank=False)
    # TODO implement or download a library for the currencies.
    amount = models.FloatField(null=False, blank=False)


class TripApproval(models.Model):
    """
    Approvals for the trips are capture in data models implemented in this class.
    By default the trip is unapproved.
    """
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE, null=False, blank=False)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=False, on_delete=models.PROTECT)
    trip_is_approved = models.BooleanField(null=False, blank=False, default=False)
    approval_date = models.DateField(null=True, blank=True, auto_now=True)
    approval_comment = models.CharField(max_length=1000, null=True, blank=True)


class TripItinerary(models.Model):
    """
    This class provides the functionality to capture the trip itinerary.
    """
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE, null=False, blank=False)
    date_of_departure = models.DateField(null=False, blank=False)
    time_of_departure = models.TimeField(null=False, blank=False)
    city_of_departure = models.CharField(max_length=40, blank=False, null=False)
    left_transit = models.BooleanField(null=False, blank=False, default=False)
    leg_status = models.BooleanField(null=False, blank=False)
    comment = models.CharField(max_length=1000, blank=True, null=True)


class ApprovalGroups(models.Model):
    """
    This class maintains the data models for approval groups and approvers. This makes it easy to
    assign and change the approvers for different travelers and travel types.
    """
    group = models.CharField(max_length=30, null=False, blank=False)
    approver = models.ForeignKey(TravelerDetails, null=False, blank=False, on_delete=models.PROTECT)
