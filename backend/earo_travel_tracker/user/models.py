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
