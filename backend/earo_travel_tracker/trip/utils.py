"""
This file defines utility classes (mostly mixins) used in this app by various views.
"""
from django.core.exceptions import ObjectDoesNotExist
from traveler.models import TravelerDetails


class TripUtilsMixin:
    """
    This mixin class checks that a user owns the trip they are trying to request approval for.
    """

    def user_owns_trip(self, trip_id):
        """
        Check if the user who submitted an approval request owns the trip.
        """
        # TODO separate boolean check and non-existent trip into different methods
        try:
            return bool(
                self.model.objects.get(id=trip_id).traveler.user_account == self.request.user
                )
        except ObjectDoesNotExist:
            self.extra_context['approval_request_error_message'] = """We can't find this trip in the
                                                                    database."""
            return self.get_success_url(trip_id)


    def get_approver(self, traveler):
        """
        Get the approver for the logged on user or return an error is the user has no
        approver set.
        """
        # TODO : user can't be their own approver.
        if traveler.approver:
            print(traveler.approver)
            return traveler.approver
        # try:
        #     print(traveler)
        #     print(TravelerDetails.objects.get(user_account=self.request.user))
        #     return TravelerDetails.objects.get(user_account=self.request.user).approver
        # except ObjectDoesNotExist:
        #     try:
        elif traveler.department.trip_approver:
            print("trying department approver")
            print(traveler.department.trip_approver)
            return traveler.department.trip_approver
        else:
            print("no approver")
            self.extra_context['approval_request_error_message'] = """We didn't find an
                                    approver set for your account. Please contact IT for
                                    this to be fixed then thereafter you can retry requesting
                                    for approval."""
                                    # TODO: make the below a get or borrow idea from form_invalid
            return self.get_success_url(self.request.trip_id)
    
    def user_is_approver(self, traveler):
        """
        Confirm that the logged on user is the approver for the request.
        """
        user = self.request.user
        return bool(user == self.get_approver(traveler))
