"""
Data models for the traveler app are defined in this file.
"""
from django.db import models
from django.conf import settings
from django.urls import reverse

LEVELS_OF_SECURITY = (
    ('1','Level 1'),
    ('1','Level 2'),
    ('3','Level 3'),
)


class Approver(models.Model):
    """
    All users who are designated as approvers have to be stored in the DB table associated with
    this model as foreign key references to their user account.
    All approvers set on other models (Departments, CountrySecurityLevel, TravelerProfile) should
    be referenced to this model.
    """
    approver = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=False,
                            blank=False)
    security_level = models.CharField(max_length=1, choices=LEVELS_OF_SECURITY, null=False,
                            blank=False, default=1, verbose_name="Security Approval Level")
    is_active = models.BooleanField(null=False, blank=True, default=True)

    def __str__(self):
        return " ".join([self.approver.first_name, self.approver.last_name])

    def get_absolute_url(self):
        """
        absolute url to an Approver instance
        """
        return reverse('view_approver', kwargs={'approver_id': self.id})

    class Meta:
        verbose_name = "Approver"
        verbose_name_plural = "Approvers"


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

    # first_name = models.CharField(max_length=20, null=False, blank=False, db_index=True)
    # last_name = models.CharField(max_length=20, null=False, blank=False)
    # date_of_birth = models.DateField(null=False, blank=False)
    department = models.ForeignKey(Departments, on_delete=models.PROTECT, null=True,
                                    blank=True)
    type_of_traveler = models.CharField(max_length=20, null=False, blank=False,
                                        choices=TRAVEL_CATEGORIES)
    nationality = models.CharField(max_length=30, null=False, blank=False)
    # is_dependant_of = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True,
    #                                     null=True, db_index=True, related_name="Guardian")
    # Allow the country_of_duty to be null when being created programmatically
    # but enforce a user to specify it when editing the profile via a form.
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
        # security level 1 approver
        print("passed arg type:", type(security_level))
        security_level = int(security_level)
        if security_level == 1:
            if self.approver is not None:
                print(self.approver) # Debug code
                return self.approver
            elif (self.department is not None and
                self.department.security_level_1_approver is not None):
                print("trying to get department approver") # debug code
                print(self.department.security_level_1_approver) # debug code
                return self.department.security_level_1_approver

        # security level 2 approver
        elif security_level == 2:
            return self.department.security_level_2_approver

        # security level 3 approver
        elif security_level == 3:
            return self.country_of_duty.security_level_3_approver
        else:
            print("no approver")  # debug code
            return None

    class Meta:
        verbose_name = "Traveler Profile"
        verbose_name_plural = "Travelers Profiles"
