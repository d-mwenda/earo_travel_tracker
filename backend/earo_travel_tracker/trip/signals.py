"""
Signals for the trip app.
Many signals will be post-save to assign various permissions.
"""
# django imports
from django.db.models.signals import post_save
from django.dispatch import receiver
# third-party app imports
from guardian.shortcuts import assign_perm
# earo_travel_tracker imports
from trip.models import Trip


@receiver(post_save, sender=Trip)
def assign_trip_perms(sender, **kwargs):
    """
    Assign the owner of a trip the rights to a trip instance.
    """
    instance = kwargs['instance']
    user = instance.traveler.user_account
    assign_perm('change_trips', user, instance)
    assign_perm('view_trips', user, instance)
    print("Permission assigned!")
