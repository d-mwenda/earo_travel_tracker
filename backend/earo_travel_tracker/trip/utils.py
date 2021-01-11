"""
This file defines utility classes (mostly mixins) used in this app by various views.
"""


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
