"""
This file contains the serializers for the traveler app.
"""
# third party imports
from rest_framework import serializers
# earo_travel_tracker imports
from traveler.models import TravelerDetails, DepartmentsModel


class TravelerDetailsSerializer(serializers.ModelSerializer):
    """
    This class serializes the TravelerDetails Model.
    """
    class Meta:
        model = TravelerDetails
        fields = ['first_name', 'last_name', 'date_of_birth', 'department',
            'type_of_traveler', 'nationality', 'is_dependant_of', 'country_of_duty',
            'contact_telephone', 'contact_email', 'user_account', 'is_managed_by']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    This class serializes DepartmentsModel.
    """
    class Meta:
        model = DepartmentsModel
        fields = ['department', 'description']
