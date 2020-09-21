"""
All views for the trip app are implemented here.
"""
# Third party imports
from rest_framework import viewsets
# Earo_travel_tracker imports
from .models import Trips, TripTravelerDependants, TripExpenses, TripApproval, TripItinerary,\
    ApprovalGroups
from .serializers import TripSerializer, TripTravelerDependantsSerializer, TripExpensesSerializer,\
    TripApprovalSerializer, TripItinerarySerializer, ApprovalGroupsSerializer

class TripViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Trips.
    """
    serializer_class = TripSerializer
    queryset = Trips.objects.all()


class TripTravelerDependantsViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Trips.
    """
    serializer_class = TripTravelerDependantsSerializer
    queryset = TripTravelerDependants.objects.all()


class TripExpensesViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Trips.
    """
    serializer_class = TripExpensesSerializer
    queryset = TripExpenses.objects.all()


class TripApprovalViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Trips.
    """
    serializer_class = TripApprovalSerializer
    queryset = TripApproval.objects.all()


class TripItineraryViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Trips.
    """
    serializer_class = TripItinerarySerializer
    queryset = TripItinerary.objects.all()


class ApproverGroupsViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Approver Groups
    """
    serializer_class = ApprovalGroupsSerializer
    queryset = ApprovalGroups.objects.all()
