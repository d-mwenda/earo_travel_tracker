"""
Signals for the trip app.
One important signal will be for creating a Traveler profile every time a
new User instance is created.
Many signals will be post-save to assign various permissions.
"""
# django imports
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
# third-party app imports
from guardian.shortcuts import assign_perm
# earo_travel_tracker imports
from traveler.models import TravelerDetails


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_traveler_profile(sender, **kwargs):
    """
    Create traveler profile for and whenever every User instance created.
    """
    instance = kwargs['instance']
    if kwargs['created']:
        TravelerDetails(
                        type_of_traveler='Employee',
                        nationality='Kenyan',
                        contact_telephone='',
                        contact_email=instance.email,
                        user_account=instance,
                    ).save()
