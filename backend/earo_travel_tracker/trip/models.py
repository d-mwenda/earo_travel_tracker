"""
Data models for the trip app are defined in this file.
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
# earo_travel_tracker imports
from traveler.models import TravelerDetails


class Trips(models.Model):
    """
    This class implements the data model for all trips taken.
    """
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

    trip_name = models.CharField(max_length=200, blank=False, null=False, db_index=True,
                                help_text="""In at most 200 characters give your trip a descriptive
                                title""")
    traveler = models.ForeignKey(TravelerDetails, on_delete=models.CASCADE, null=False, blank=True)
    type_of_travel = models.CharField(max_length=15, null=False, blank=False, choices=TRAVEL_TYPES)
    category_of_travel = models.CharField(max_length=15, null=False, blank=False,
                                            choices=TRAVEL_CATEGORIES)
    reason_for_travel = models.CharField(max_length=1000, null=False, blank=False, help_text=
                                "Use less than 1000 characters to describe the reasons for travel")
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    is_mission_critical = models.BooleanField(null=False, blank=False)
    is_travel_completed = models.BooleanField(null=False, blank=False, default=False)
    created_on = models.DateTimeField(auto_now=True, null=False)
    scope_of_work = models.FileField(upload_to="uploads/scope_of_work/%Y/%m/%d/", verbose_name="Scope of Work",
                                null=True, blank=False)

    def get_absolute_url(self):
        """
        Defines the url for the details view of this model.
        """
        return reverse('u_trip_details', args=(self.id,))

    def __str__(self):
        return self.trip_name


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
    trip = models.OneToOneField(Trips, on_delete=models.CASCADE, null=False, blank=False)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                on_delete=models.PROTECT, verbose_name="Approved by")
    trip_is_approved = models.BooleanField(null=False, blank=False, default=False,
                                            verbose_name='Approval')
    approval_request_date = models.DateField(null=False, blank=True, auto_now_add=True)
    approval_date = models.DateField(null=True, blank=True)
    approval_comment = models.CharField(max_length=1000, null=True, blank=True,
                                        verbose_name='Comment')


class TripItinerary(models.Model):
    """
    This class provides the functionality to capture the trip itinerary.
    """
    LEG_STATUSES = (
        ('Complete', 'Incomplete'),
        ('Incomplete', 'Incomplete'),
    )

    TRAVEL_MODES = (
        ('Air', 'Air'),
        ('Land', 'Land'),
        ('Water', 'Water'),
    )

    trip = models.ForeignKey(Trips, on_delete=models.CASCADE, null=False, blank=False)
    date_of_departure = models.DateField(null=False, blank=False)
    time_of_departure = models.TimeField(null=False, blank=False)
    city_of_departure = models.CharField(max_length=40, blank=False, null=False)
    destination = models.CharField(max_length=50, null=False, blank=False)
    mode_of_travel = models.CharField(max_length=10, null=False, blank=False, choices=TRAVEL_MODES)
    leg_status = models.CharField(max_length=10, null=False, blank=False,
                                choices=LEG_STATUSES, default='Incomplete')
    comment = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return ", ".join([
                        self.trip.trip_name,
                    " - ".join([self.city_of_departure, self.destination]),
                    "Leg"
                    ])
  
    def get_absolute_url(self):
        """
        Unique and permanent url to an instance of this model. Given that there's no plan to
        implement the Detailview of an Itinerary leg yet, the url will resolve to the Detail
        View of the trip to which the instance belongs.
        TODO. This will change when the URL conf of the itinerary changes to include trip ID.
        """
        return reverse('u_trip_details', kwargs={'trip_id':self.trip.id})


class ApprovalGroups(models.Model):
    """
    This class maintains the data models for approval groups and approvers. This makes it easy to
    assign and change the approvers for different travelers and travel types.
    """
    group = models.CharField(max_length=30, null=False, blank=False)
    approver = models.ForeignKey(TravelerDetails, null=False, blank=False, on_delete=models.PROTECT)
