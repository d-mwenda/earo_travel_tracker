"""
this script defines a command to syncronize AD users with traveler user accounts.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
# earo-travel-tracker imports
from traveler.models import TravelerProfile


class Command(BaseCommand):
    """
    Definition of the synctravers command.

    This command is redundant as creating traveler profiles is now done by a post save signal on the
    User model.
    """
    # TODO: command error when any invalid args are passed to the command
    # TODO: implement manage.py synctraveler singleuser run by logged on users with no traver profile
    help = 'Syncronize AUTH_USER_MODEL objects with TravelerDetail Model to link user accounts.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        for user in user_model.objects.all():
            try:
                TravelerProfile.objects.get(user_account=user.id)
            except TravelerProfile.DoesNotExist:
                TravelerProfile(
                    type_of_traveler='Employee',
                    nationality='Kenyan',
                    contact_telephone='',
                    contact_email=''.join([user.first_name, ".", user.last_name, "@crs.org"]),
                    user_account=user,
                ).save()
                self.stdout.write(self.style.SUCCESS(
                    '"%s"\'s profile successfully linked' % user.username
                    )
                )
