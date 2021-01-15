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

    def get_approver(self, traveler):
        """
        Get the approver for the logged on user or return None if the user has no
        approver set.
        """
        if traveler.approver is not None:
            print(traveler.approver) # Debug code
            return traveler.approver
        elif traveler.department is not None and traveler.department.trip_approver is not None:
            print("trying to get department approver") # debug code
            print(traveler.department.trip_approver) # debug code
            return traveler.department.trip_approver
        print("no approver")  # debug code
        return None

    def user_is_approver(self, traveler):
        """
        Confirm that the logged on user is the approver for the request.
        """
        user = self.request.user
        return bool(user == self.get_approver(traveler))

    def get_line_manager(self, traveler):
        """
        Get the line manager of a user or return None if none is set.
        """
        if traveler.is_managed_by is not None:
            print(traveler.is_managed_by) # Debug code
            return traveler.is_managed_by
        print("No line manager")  # debug code
        return None

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
        if self.object is None:
            trip = self.get_object()
        return

    def invalidate_trip_approval(self):
        """
        Reset all approvals for a trip instance.
        This is especially useful when a user modifies any detail of a trip.
        """
        pass


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
        Check if a trip is approved. This helps in rendering the template
        so that appropriate buttons and messages are displayed.
        """
        status = None
        try:
            queryset = TripApproval.objects.get(trip=self.get_object())
            if queryset.trip_is_approved:
                status = 'Approved'
            else:
                status = 'Unapproved'
        except TripApproval.DoesNotExist:
            status = 'Not requested'
        return status
