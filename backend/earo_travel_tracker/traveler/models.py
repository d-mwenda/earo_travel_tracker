"""
Data models for the traveler app are defined in this file.
"""
from django.db import models
from django.conf import settings
from django.urls import reverse


class Departments(models.Model):
    """
    This class will implement departments model in the organization. This can also be
    functional units as my be appropriate for intents and purposes of this software.
    """
    department = models.CharField(max_length=50, null=False, blank=False, db_index=True)
    description = models.CharField(max_length=200, null=False, blank=False)
    trip_approver = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                            on_delete=models.PROTECT)

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
    country_of_duty = models.CharField(max_length=40, null=True, blank=False,
                                        verbose_name="Country of duty / residence")
    contact_telephone = models.CharField(max_length=20, null=False, blank=False)
    contact_email = models.CharField(max_length=70, null=False, blank=True)
    user_account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,
                            blank=True, null=True)
    is_managed_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                                    db_index=True, verbose_name="Line Manager",
                                    related_name='Line_Manager')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True,
                                null=True, related_name='trip_approver')

    def __str__(self):
        if self.user_account:
            return " ".join([self.user_account.first_name, self.user_account.last_name])
        return self.id

    def get_absolute_url(self):
        return reverse('u_traveler_details', args=(self.id,))

    class Meta:
        verbose_name = "Traveler Profile"
        verbose_name_plural = "Travelers Profiles"