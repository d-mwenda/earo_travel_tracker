"""
Signals for the trip app.
Many signals will be post-save to assign various permissions.
"""
import logging
# django imports
from django.db.models.signals import post_save
from django.dispatch import receiver
# third-party app imports
from guardian.shortcuts import assign_perm
# earo_travel_tracker imports
from trip.models import Trip, TripPOET

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Trip)
def assign_trip_perms(sender, **kwargs):
    """
    Assign the owner of a trip the rights to a trip instance.
    """
    trip = kwargs['instance']
    user = trip.traveler.user_account
    assign_perm('change_trip', user, trip)
    assign_perm('view_trip', user, trip)
    logger.debug("Change permission for the %s instance assigned to trip owner", sender)

@receiver(post_save, sender=TripPOET)
def assign_trip_poet_perms(sender, **kwargs):
    """
    Assign the owner of a trip the rights to a trip instance.
    """
    trip_poet = kwargs['instance']
    user = trip_poet.trip.traveler.user_account
    assign_perm('change_trippoet', user, trip_poet)
    assign_perm('view_trippoet', user, trip_poet)
    logger.debug("Change permission for the %s instance assigned to trip owner", sender)

@receiver(post_save, sender=TripPOET)
def assign_trip_itinerary_perms(sender, **kwargs):
    """
    Assign the owner of a trip the rights to a trip instance.
    """
    trip_itinerary = kwargs['instance']
    user = trip_itinerary.trip.traveler.user_account
    assign_perm('change_trippoet', user, trip_itinerary)
    assign_perm('view_trippoet', user, trip_itinerary)
    logger.debug("Change permission for the %s instance assigned to trip owner", sender)
