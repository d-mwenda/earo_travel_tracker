"""
Data models for the trip app are defined in this file.
"""
from django.db import models
from django.urls import reverse
# earo_travel_tracker imports
from traveler.models import TravelerProfile, Approver, LEVELS_OF_SECURITY


class Trip(models.Model):
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
    traveler = models.ForeignKey(TravelerProfile, on_delete=models.CASCADE, null=False, blank=True)
    type_of_travel = models.CharField(max_length=20, null=False, blank=False, choices=TRAVEL_TYPES)
    category_of_travel = models.CharField(max_length=15, null=False, blank=False,
                            choices=TRAVEL_CATEGORIES)
    reason_for_travel = models.CharField(max_length=1000, null=False, blank=False, help_text=
                            "Use less than 1000 characters to describe the reasons for travel")
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    is_mission_critical = models.BooleanField(null=False, blank=False)
    is_travel_completed = models.BooleanField(null=False, blank=False, default=False)
    created_on = models.DateTimeField(auto_now=True, null=False)
    scope_of_work = models.FileField(upload_to="media/uploads/scope_of_work/%Y/%m/%d/",
                            verbose_name="Scope of Work", null=True, blank=False)
    security_level = models.CharField(max_length=1,null=False, choices=LEVELS_OF_SECURITY,
                            default=1)
    # TODO make default on form = traveler.country_of_duty.security_level). maybe form.initial
    approval_complete = models.BooleanField(null=False, default=False,
                            verbose_name="Is approval Complete?")


    def get_absolute_url(self):
        """
        Defines the url for the details view of this model.
        """
        return reverse('u_trip_details', args=[str(self.id)])

    def __str__(self):
        return self.trip_name

    def is_valid_for_approval(self):
        """
        Check that the trip is valid to be approved.
        """
        if not TripPOET.objects.filter(trip__id=self.id):
            return False
        if not TripItinerary.objects.filter(trip__id=self.id):
            return False
        return True

    def is_owned_by(self, user):
        """
        Check if a user owns the trip.
        Takes in a settings.USER_MODEL instance as an argument.
        """
        return bool(self.traveler.user_account == user)

    def request_approval(self, security_level, approver):
        """
        Create a TripApproval instance and send email to approver and requester.
        """
        approval_request = TripApproval(
            trip=self,
            security_level=security_level,
            approver=approver
        )
        approval_request.save()
        return approval_request

    def invalidate_approval(self):
        """
        Invalidate all approvals for a trip instance.
        This is especially useful when a user modifies any detail of a trip.

        check if trip is approved, revert to False
        check all exisiting associated TripApproval instances and invalidate them

        this should be used in a view where the object is a Trip instance.
        """
        if self.approval_complete:
            self.approval_complete = False
            self.save()
        approvals = TripApproval.objects.filter(trip=self).filter(is_valid=True)
        for approval in approvals:
            approval.is_valid = False
            approval.save()

    def get_approval_status(self):
        """
        Check which stage in the approval workflow a trip is in.
        can be:
            Not requested
            Approved
            Awaiting Level 1 Approval
            Awaiting Level 2 Approval
            Awaiting Level 3 Approval
        """
        # check if trip is already completely approved.
        if self.approval_complete:
            return "Approved"

        # Check which stage the unapproved trip is in the approval process
        queryset = TripApproval.objects.filter(trip__id=self.id).filter(is_valid=True)
        if queryset:
            # get the last approval and check for which security level it belongs.
            queryset = queryset.order_by("-approval_request_date")[0]
            if queryset.security_level == str(1):
                return "Awaiting Level 1 Approval"
            if queryset.security_level == str(2):
                return "Awaiting Level 2 Approval"
            return "Awaiting Level 3 Approval"
        return 'Not requested'

    def get_next_security_level(self):
        """
        Check which is the next approval level and return it.
        """
        # TODO add filter to check last approval is True and valid
        approvals = TripApproval.objects.filter(trip__id=self.id).order_by("-approval_request_date")
        # approvals.filter(is_valid=True).filter(trip_is_approved=True)
        if approvals:
            last_approval = approvals[0]
            if last_approval.security_level == self.security_level:
                return None
            return int(last_approval.security_level) + 1
        return 1

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

class TripPOET(models.Model):
    """
    Capture the budget details for a trip. This is to enable an approver know where
    the trip cost will be charged.
    """
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, blank=False, null=False)
    project = models.CharField(max_length=6, null=False, blank=False, db_index=True)
    task = models.CharField(max_length=3, null=False, blank=False)

    def __str__(self):
        return self.trip.trip_name

    def get_absolute_url(self):
        """
        Unique and permanent url to an instance of this model. Given that there's no plan to
        implement the Detailview of an Itinerary leg yet, the url will resolve to the Detail
        View of the trip to which the instance belongs.
        """
        return reverse('u_trip_details', kwargs={'trip_id':self.trip.id})

    class Meta:
        verbose_name = "Trip POET Details"
        verbose_name_plural = "Trip POET Details"


class TripTravelerDependants(models.Model):
    """
    Dependants travelling with an employee are captured in this class.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=False, blank=False)
    dependants_travelling = models.ForeignKey(TravelerProfile, on_delete=models.CASCADE,
                                    null=False, blank=False)


class TripApproval(models.Model):
    """
    Approvals for the Trips are capture in data models implemented in this class.
    By default the trip is unapproved when first created.

    security_level defines the security level for which an instance approves.
    is_valid tells whether an approval or request for approval is valid.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=False, blank=False,
                                db_index=True, related_name="trip_approvals")
    approval_request_date = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    is_valid = models.BooleanField(null=False, blank=True, default=True,
                                verbose_name="Approval validity")
    approver = models.ForeignKey(Approver, blank=False, null=True,
                                on_delete=models.PROTECT, verbose_name="Approved by")
    security_level = models.CharField(max_length=1,null=False, choices=LEVELS_OF_SECURITY,
                                default=1)
    trip_is_approved = models.BooleanField(null=False, blank=False, default=False,
                                verbose_name='Approval')
    approval_date = models.DateField(null=True, blank=True)
    approval_comment = models.CharField(max_length=1000, null=True, blank=True,
                                verbose_name='Comment')

    class Meta:
        verbose_name = "Trip Approval"
        verbose_name_plural = "Trips Approvals"


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
        ('Road', 'Road'),
        ('Water', 'Water'),
    )

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=False, blank=False)
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
        """
        return reverse('u_trip_details', kwargs={'trip_id':self.trip.id})

    #  TODO fix validation and uncomment this
    # def clean(self):
    #     """
    #     Check that the TripItinerary instance date_of_departure is within the trip dates.
    #     """
    #     super().clean()
        # if self.date_of_departure < self.trip.start_date:
        #     raise ValidationError("This date cannot be before the trip start date.")
        # if self.date_of_departure > self.trip.end_date:
        #     raise ValidationError("This date cannot be later than the trip end date.")

    # def save(self, **kwargs):
    #     """Add support for custom validation implemented in this model."""
    #     self.full_clean()
    #     return super().save(**kwargs)

    class Meta:
        verbose_name = "Trip Itinerary"
        verbose_name_plural = "Trips Itineraries"
