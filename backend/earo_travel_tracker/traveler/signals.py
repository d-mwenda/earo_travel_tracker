"""
Signals for the trip app.
One important signal will be for creating a Traveler profile every time a
new User instance is created.
Many signals will be post-save to assign various permissions.
"""
import logging
# django imports
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import Group
# third-party app imports
from guardian.shortcuts import assign_perm, get_anonymous_user
# earo_travel_tracker imports
from traveler.models import TravelerProfile

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_traveler_profile(sender, **kwargs):
    """
    Create traveler profile for and whenever every User instance created.
    Assign the user all the basic permissions for a traveler by adding them
    to traveler group.
    """
    user = kwargs['instance']
    if kwargs['created'] and user != get_anonymous_user():
        profile = TravelerProfile(
                    type_of_traveler='Employee',
                    nationality='Kenyan',
                    contact_telephone='',
                    contact_email=user.email,
                    user_account=user,
        ).save()
        logger.debug("Created profile for %s", user.username)
        assign_perm("traveler.change_travelerprofile", user, profile)
        logger.debug("Granted %s permission to change own profile", user.username)
        try:
            travelers = Group.objects.get(name='travelers')
            travelers.user_set.add(user)
        except Group.DoesNotExist:
            logger.error("Travelers group doesn't exist. " \
                "Create the group and assign it the proper permissions.")
