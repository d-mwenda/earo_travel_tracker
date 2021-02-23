"""
Model tests for models in the Traveler app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_anonymous_user
from traveler.models import TravelerProfile


class TestCreateTravelerProfileSignal(TestCase):
    """
    Test different functionality of the Traveler Profile Model
    """
    def setUp(self):
        user_model = get_user_model()
        self.travelers_group = Group.objects.create(name="travelers")
        user = user_model.objects.create(username='testuser', password="pass1234")
        self.user = get_object_or_404(user_model, pk=user.id)
        try:
            self.traveler = TravelerProfile.objects.get(user_account=self.user)
        except TravelerProfile.DoesNotExist:
            # if this exception is raised, the tests cannot continue
            self.fail("The user profile was not created. "\
                "The traveler.signals.create_traveler_profile signal isn't working")

    def test_traveler_profile_created(self):
        """
        Test that the User Model post save signal creates a traveler profile for every new user.
        """
        self.assertEqual(self.user, self.traveler.user_account)

    def test_traveler_profile_permission_granted(self):
        """
        Test that the Traveler post save signal grants the user permissions to their own profile.
        """
        self.assertTrue(self.user.has_perm("change_travelerprofile", self.traveler))

    def test_user_added_to_travelers_group(self):
        """
        Test that whenever a new user is created they are added to 'travelers' group
        """
        self.assertTrue(self.user.groups.filter(name=self.travelers_group).exists())

    def test_anonymous_has_no_traveler_profile(self):
        """
        Verify that the anonymous user doesn't get a traveler profile created.
        """
        anonymous_user = get_anonymous_user()
        self.assertRaises(TravelerProfile.DoesNotExist,
                TravelerProfile.objects.get,
                user_account=anonymous_user)
