"""
This file defines utility classes (mostly mixins) used in this app by various views.
"""
from .models import TripPOET, TripItinerary, TripApproval


class TripUtilsMixin:
    """
    This mixin class checks that a user owns the trip they are trying to request approval for.
    """

    def user_owns_trip(self, trip):
        """
        Check if the logged on user owns the trip.
        Takes in a Trip Model instance as an argument.
        """
        return bool(trip.traveler.user_account == self.request.user)

    def user_is_approver(self, traveler, security_level=1):
        """
        Confirm that the logged on user is the approver for the request.
        """
        user = self.request.user
        set_approver = self.get_approver(traveler, security_level=security_level)
        if set_approver is None:
            return False
        return bool(user == set_approver.approver)

    def is_line_manager(self, traveler):
        """
        Check that the logged on user is the line manager of a traveler.
        """
        user = self.request.user
        return bool(user == self.get_line_manager(traveler))

    def is_approved_trip(self):
        """
        Check whether a trip is already approved.
        """
        trip = self.object or self.get_object()
        return trip.approval_complete

    def invalidate_trip_approval(self):
        """
        Invalidate all approvals for a trip instance.
        This is especially useful when a user modifies any detail of a trip.

        check if trip is approved, revert to False
        check all exisiting associated TripApproval instances and invalidate them

        this should be used in a view where the object is a Trip instance.
        """
        trip = self.object or self.get_object()
        if trip.approval_complete:
            trip.approval_complete = False
            trip.save()
        approvals = self.approval_model.objects.filter(trip=trip).filter(is_valid=True)
        for approval in approvals:
            approval.is_valid = False
            approval.save()
        self.object = trip

    def is_valid_for_approval(self):
        """
        Check that the trip is valid to be approved.
        """
        trip = self.object or self.get_object()
        if not TripPOET.objects.filter(trip=trip):
            return False
        if not TripItinerary.objects.filter(trip=trip):
            return False
        return True

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
        trip = self.object or self.get_object()

        # check if trip is already completely approved.
        if trip.approval_complete:
            return "Approved"

        # Check which stage the unapproved trip is in the approval process
        queryset = TripApproval.objects.filter(trip=trip).filter(is_valid=True)
        if queryset:
            # get the last approval and check for which security level it belongs.
            queryset = queryset.order_by("-approval_request_date")[0]
            if queryset.security_level == str(1):
                return "Awaiting Level 1 Approval"
            if queryset.security_level == str(2):
                return "Awaiting Level 2 Approval"
            return "Awaiting Level 3 Approval"
        return 'Not requested'

    @staticmethod
    def get_next_security_level(trip):
        """
        Check which is the next approval level and return it.
        """
        approvals = TripApproval.objects.filter(trip=trip).order_by("-approval_request_date")
        if approvals:
            last_approval = approvals[0]
            if last_approval.security_level == trip.security_level:
                return None
            return int(last_approval.security_level) + 1
        return 1

    @staticmethod
    def request_approval(trip, security_level):
        """
        Create a TripApproval instance and send email to approver and requester.
        """
        approval_request = TripApproval(trip=trip, security_level=security_level)
        approval_request.save()
        return approval_request

    @staticmethod
    def get_approver(traveler, security_level=1):
        """
        Get the approver for the logged on user or return None if the user has no
        approver set.
        """
        # security level 1 approver
        if security_level == 1:
            if traveler.approver is not None:
                print(traveler.approver) # Debug code
                return traveler.approver
            if (traveler.department is not None and
                traveler.department.security_level_1_approver is not None):
                print("trying to get department approver") # debug code
                print(traveler.department.security_level_1_approver) # debug code
                return traveler.department.security_level_1_approver
            print("no approver")  # debug code
            return None

        # security level 2 approver
        if security_level == 2:
            return traveler.department.security_level_2_approver

        # security level 3 approver
        if security_level == 3:
            return traveler.country_of_duty.security_level_3_approver

    @staticmethod
    def get_line_manager(traveler):
        """
        Get the line manager of a user or return None if none is set.
        """
        if traveler.is_managed_by is not None:
            print(traveler.is_managed_by) # Debug code
            return traveler.is_managed_by
        print("No line manager")  # debug code
        return None
