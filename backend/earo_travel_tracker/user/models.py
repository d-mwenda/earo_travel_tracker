"""
Implementation of auth for the application.
"""
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    This is the User model implementation for the application.
    It implements the __str__ and inherits everything else from AbstractUser.
    """
    def __str__(self):
        return " ".join([self.first_name, self.last_name])

    def is_an_approver(self):
        """
        Check that user is an approver.
        """
        try:
            self.approver
            return True
        except User.approver.RelatedObjectDoesNotExist:
            return False
