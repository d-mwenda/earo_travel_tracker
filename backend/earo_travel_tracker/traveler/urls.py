"""
All url mappings for the traveler app are defined here
"""

# Third party app imports
from rest_framework import routers
# Earo_travel_tracker imports
from .views import TravelerViewSet


router = routers.SimpleRouter()
router.register(r'traveler', TravelerViewSet)
api_url_patterns = router.urls
