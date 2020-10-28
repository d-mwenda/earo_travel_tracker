"""
This file defines utility classes (mostly mixins) used in this app by various views.
"""
from django.core.exceptions import ObjectDoesNotExist


class UserOwnsTripMixin:
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
