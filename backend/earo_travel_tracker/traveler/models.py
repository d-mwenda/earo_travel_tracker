"""
Data models for the traveler app are defined in this file.
"""
from django.db import models
from django.conf import settings
from django.urls import reverse


class DepartmentsModel(models.Model):
    """
    This class will implement departments model in the organization. This can also be
    functional units as my be appropriate for intents and purposes of this software.
    """
    department = models.CharField(max_length=50, null=False, blank=False, db_index=True)
    description = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.department

    def get_absolute_url(self):
        """
        Define the url for model instances.
        """
        return reverse('u_department_details', args=(self.id,))


class TravelerDetails(models.Model):
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

    first_name = models.CharField(max_length=20, null=False, blank=False, db_index=True)
    last_name = models.CharField(max_length=20, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    department = models.ForeignKey(DepartmentsModel, on_delete=models.PROTECT, null=False,
                                    blank=False)
    type_of_traveler = models.CharField(max_length=20, null=False, blank=False,
                                        choices=TRAVEL_CATEGORIES)
    nationality = models.CharField(max_length=30, null=False, blank=False)
    is_dependant_of = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True,
                                        null=True, db_index=True, related_name="Guardian")
    country_of_duty = models.CharField(max_length=40, null=False, blank=False,
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
        return ", ".join([self.last_name, self.first_name])

    def get_absolute_url(self):
        return reverse('u_traveler_details', args=(self.id,))
