"""
This file defines utility classes (mostly mixins) used in this app by various views.
"""
from .models import TripApproval


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
            print("returning none")
            return False
        print("set approver ", set_approver.approver)
        return bool(user == set_approver.approver)


    def get_approval_status(self):
        """
        Check which stage in the approval workflow a trip is in.
        can be:
            Not requested
            Approved
            Awaiting Level 1 Approval
            Awaiting Level 2 Approval
            Awaiting Level 3 Approval
        # TODO can be a method in the Trip model
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
        TODO can be a method in the Trip or Trip approval model
        """
        approvals = TripApproval.objects.filter(trip=trip).order_by("-approval_request_date")
        if approvals:
            last_approval = approvals[0]
            if last_approval.security_level == trip.security_level:
                return None
            return int(last_approval.security_level) + 1
        return 1

    # @staticmethod
    # def get_approver(traveler, security_level=1):
    #     """
    #     Get the approver for the logged on user or return None if the user has no
    #     approver set.
    #     TODO can be a model in the Trip or Trip approval model, or even Traveler model
    #     """
    #     # security level 1 approver
    #     if security_level == 1:
    #         if traveler.approver is not None:
    #             print(traveler.approver) # Debug code
    #             return traveler.approver
    #         if (traveler.department is not None and
    #             traveler.department.security_level_1_approver is not None):
    #             print("trying to get department approver") # debug code
    #             print(traveler.department.security_level_1_approver) # debug code
    #             return traveler.department.security_level_1_approver
    #         print("no approver")  # debug code

    #     # security level 2 approver
    #     elif security_level == 2:
    #         return traveler.department.security_level_2_approver

    #     # security level 3 approver
    #     elif security_level == 3:
    #         return traveler.country_of_duty.security_level_3_approver
    #     else:
    #         return None
