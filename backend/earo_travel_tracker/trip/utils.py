"""
This file defines utility classes (mostly mixins) used in this app by various views.
"""


class TripUtilsMixin:
    """
    This mixin class checks that a user owns the trip they are trying to request approval for.
    """

    def user_is_approver(self, traveler, security_level=1):
        """
        Confirm that the logged on user is the approver for the request.
        TODO can be in the User model
        """
        user = self.request.user
        set_approver = traveler.get_approver(security_level=security_level)
        if set_approver is None:
            print("no approver") # debug code
            return False
        print("set approver ", set_approver.approver) # debug code
        return bool(user == set_approver.approver)
