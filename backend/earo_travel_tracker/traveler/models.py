"""
Data models for the traveler app are defined in this file.
"""
import logging
# django imports
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Group
from django.utils import timezone

LEVELS_OF_SECURITY = (
    ('1','Level 1'),
    ('2','Level 2'),
    ('3','Level 3'),
)


logger = logging.getLogger(__name__)

class Approver(models.Model):
    """
    All users who are designated as approvers have to be stored in the DB table associated with
    this model as foreign key references to their user account.
    All approvers set on other models (Departments, CountrySecurityLevel, TravelerProfile) should
    be referenced to this model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=False,
                            blank=False, related_name="approver")
    security_level = models.CharField(max_length=1, choices=LEVELS_OF_SECURITY, null=False,
                            blank=False, default=1, verbose_name="Security Approval Level")
    is_active = models.BooleanField(null=False, blank=True, default=True)

    def __str__(self):
        return " ".join([self.user.first_name, self.user.last_name])

    def get_absolute_url(self):
        """
        absolute url to an Approver instance
        """
        return reverse('view_approver', kwargs={'approver_id': self.id})

    def active_delegation_exists(self):
        """
        Check if there is an existing active delegation.
        """
        return ApprovalDelegation.objects.filter(approver=self).filter(active=True).exists()

    def get_delegate(self):
        """Get the approver to whom approval has been delegated"""
        return self.get_active_delegation().approver

    def get_active_delegation(self):
        """Get the active delegation"""
        return ApprovalDelegation.objects.filter(approver=self, active=True)[0]

    def add_to_approvers_group(self):
        """
        Add approver to approvers group when an approver is created.
        """
        if self._state.adding:
            try:
                approvers = Group.objects.get(name='approvers')
                approvers.user_set.add(self.user)
            except Group.DoesNotExist:
                logger.error("Approvers group doesn't exist. "
                    "Create the group and assign it the proper permissions.")

    def save(self, *args, **kwargs):
        self.add_to_approvers_group()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Approver"
        verbose_name_plural = "Approvers"


class ApprovalDelegation(models.Model):
    """
    This class implements delegation of approval rights.
    """
    approver = models.ForeignKey(Approver, on_delete=models.PROTECT,
            related_name="delegating_approver", null=False, blank=False, db_index=True)
    delegate = models.ForeignKey(Approver, on_delete=models.PROTECT,
            related_name="delegate", null=False, blank=False, db_index=True)
    reason_for_delegation = models.TextField(max_length=500, blank=False, null=False)
    reason_for_revocation = models.TextField(max_length=500, blank=False, null=False)
    start_date = models.DateField(null=False, blank=False, default=timezone.now)
    end_date = models.DateField(null=False, blank=False)
    active = models.BooleanField(default=True, null=False)

    def get_absolute_url(self):
        """Permalink to an objects details"""
        return reverse('u_trip_details', kwargs={'approval_delegation_id':self.id})

    def revoke_approval_delegation(self, reason_for_revocation):
        """
        Enables an approver to revoke an existing delegation of their approval rights.
        """
        self.active = False
        self.reason_for_revocation = reason_for_revocation
        self.end_date = timezone.now().today()
        self.save()


class Departments(models.Model):
    """
    This class will implement departments model in the organization. This can also be
    functional units as my be appropriate for intents and purposes of this software.
    """
    department = models.CharField(max_length=50, null=False, blank=False, db_index=True)
    description = models.CharField(max_length=200, null=False, blank=False)
    security_level_1_approver = models.ForeignKey(Approver, on_delete=models.PROTECT,null=True,
                            blank=True, related_name="security_level_1_approver")
    security_level_2_approver = models.ForeignKey(Approver, on_delete=models.PROTECT,null=True,
                            blank=True, related_name="security_level_2_approver")


    def __str__(self):
        return self.department

    def get_absolute_url(self):
        """
        Define the url for model instances.
        """
        return reverse('u_department_details', args=(self.id,))

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class CountrySecurityLevel(models.Model):
    """
    This model lists countries and their associated security levels.
    """
    country = models.CharField(max_length=50, null=False, blank=False)
    security_level = models.CharField(max_length=1, choices=LEVELS_OF_SECURITY, null=False,
                            blank=False)
    security_level_3_approver = models.ForeignKey(Approver, null=True, blank=True,
                            on_delete=models.PROTECT)

    def __str__(self):
        return self.country

    def get_absolute_url(self):
        """
        Absolute URL to a Country Security Level instance.
        """
        return reverse('view_country', kwargs={"country_id": self.id})

    class Meta:
        verbose_name = "Country Security Level"
        verbose_name_plural = "Countries Security Levels"


class TravelerProfile(models.Model):
    """
    This model defines details of travelers. They can be employees, dependants of employees,
    consultants and partners. When it's employees or partners, there's a ONETOONE mapping to
    the USER model to associate with the travelers login account.
    """
    TRAVEL_CATEGORIES = (
        ('Employee', 'Employee'),
        ('Dependant', 'Consultant'),
        ('Consultant', 'Consultant'),
        ('Partners', 'Partners'),
    )

    department = models.ForeignKey(Departments, on_delete=models.PROTECT, null=True,
                                    blank=True)
    type_of_traveler = models.CharField(max_length=20, null=False, blank=False,
                                        choices=TRAVEL_CATEGORIES)
    nationality = models.CharField(max_length=30, null=False, blank=False)
    country_of_duty = models.ForeignKey(CountrySecurityLevel , null=True, blank=False,
                            on_delete=models.PROTECT, verbose_name="Country of duty / residence")
    contact_telephone = models.CharField(max_length=20, null=False, blank=False)
    contact_email = models.CharField(max_length=70, null=False, blank=True)
    user_account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,
                            blank=True, null=True)
    is_managed_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                                    db_index=True, verbose_name="Line Manager",
                                    related_name='Line_Manager')
    approver = models.ForeignKey(Approver, on_delete=models.PROTECT, blank=True,
                                null=True, related_name='trip_approver')

    def __str__(self):
        if self.user_account:
            return " ".join([self.user_account.first_name, self.user_account.last_name])
        return self.id

    def get_absolute_url(self):
        """Return the absolute url of the detail view of an instance."""
        return reverse('u_traveler_details', args=[(self.id)])

    def is_line_managed_by(self, user):
        """
        Check that the logged on user is the line manager of a traveler.
        The user argument should be an instance of settings.USER_MODEL
        """
        return bool(self.is_managed_by == user)

    def get_approver(self, security_level=1):
        """
        Get the approver for a traveler profile, given the security level
        return None if no approver is set.
        """
        approver = None
        # security level 1 approver
        print("passed arg type:", type(security_level)) # debugging code
        security_level = int(security_level)
        if security_level == 1:
            if self.approver is not None:
                print(self.approver) # Debug code
                approver = self.approver
            elif (self.department is not None and
                self.department.security_level_1_approver is not None):
                print("trying to get department approver") # debug code
                print(self.department.security_level_1_approver) # debug code
                approver = self.department.security_level_1_approver

        # security level 2 approver
        elif security_level == 2:
            approver = self.department.security_level_2_approver

        # security level 3 approver
        elif security_level == 3:
            approver = self.country_of_duty.security_level_3_approver
            print(f"sec level 3 {approver}")
        else:
            print("Invalid Security Level")  # debug code
            return None

        # check if approval has been delegated.
        if approver is not None and approver.active_delegation_exists():
            return approver.get_delegate()
        return approver

    class Meta:
        verbose_name = "Traveler Profile"
        verbose_name_plural = "Travelers Profiles"
