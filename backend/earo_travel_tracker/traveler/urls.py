"""
All url mappings for the traveler app are defined here
"""
from django.urls import path
# Third party app imports
from rest_framework import routers
# Earo_travel_tracker imports
from .views import TravelerViewSet, DepartmentViewSet


router = routers.SimpleRouter()
router.register(r'traveler', TravelerViewSet)
router.register(r'departments', DepartmentViewSet)
api_url_patterns = router.urls

urlpatterns = [
    
]
