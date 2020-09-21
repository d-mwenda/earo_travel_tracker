"""
This file contains the serializers for the trip app.
"""
# third party imports
from rest_framework import serializers
# earo_travel_tracker imports
from trip.models import Trips, TripTravelerDependants, TripExpenses, TripApproval, TripItinerary,\
    ApprovalGroups


class TripSerializer(serializers.ModelSerializer):
    """
    This class serializes the Trip model.
    """
    class Meta:
        model = Trips
        fields = ['traveler', 'type_of_travel', 'categories_of_travel', 'mode_of_travel',
                'reason_for_travel', 'is_mission_critical', 'is_travel_completed']



class TripTravelerDependantsSerializer(serializers.ModelSerializer):
    """
    This class serializes the TripTravelerDependants model.
    """
    class Meta:
        model = TripTravelerDependants
        fields = ['trip', 'dependants_travelling']


class TripExpensesSerializer(serializers.ModelSerializer):
    """
    This class serializes the TripExpenses model.
    """
    class Meta:
        model = TripExpenses
        fields = ['trip', 'type_of_expense', 'currency', 'amount']


class TripApprovalSerializer(serializers.ModelSerializer):
    """
    This class serializes the TripApproval model.
    """
    class Meta:
        model = TripApproval
        fields = ['trip', 'approver', 'trip_is_approved', 'approval_date', 'approval_comment']


class TripItinerarySerializer(serializers.ModelSerializer):
    """
    This class serializes the TripItinerary model.
    """
    class Meta:
        model = TripItinerary
        fields = ['trip', 'date_of_departure', 'time_of_departure', 'city_of_departure',
                'left_transit', 'leg_status', 'comment']


class ApprovalGroupsSerializer(serializers.ModelSerializer):
    """
    This class serializes the ApprovalGroups model.
    """
    class Meta:
        model = ApprovalGroups
        fields = ['group', 'approver']