"""
This file provides all view functionality for the traveler app.
"""
# Third party apps imports
from rest_framework import viewsets
# Earo_travel_tracker imports
from .models import TravelerDetails
from .serializers import TravelerDetailsSerializer


class TravelerViewSet(viewsets.ModelViewSet):
    """
    This class provides the requisite functionality to manipulate traveler details.
    """
    queryset = TravelerDetails.objects.all()
    serializer_class = TravelerDetailsSerializer
