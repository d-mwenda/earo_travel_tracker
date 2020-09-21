"""
All url mappings for the trip app are defined here
"""

# Third party app imports
from rest_framework import routers
# Earo_travel_tracker imports
from .views import TripViewSet, TripTravelerDependantsViewSet, TripExpensesViewSet,\
    TripApprovalViewSet, TripItineraryViewSet, ApproverGroupsViewSet


router = routers.SimpleRouter()
router.register(r'trips', TripViewSet)
router.register(r'trip-traveler-dependants', TripTravelerDependantsViewSet)
router.register(r'trip-expenses', TripExpensesViewSet)
router.register(r'trip-approval', TripApprovalViewSet)
router.register(r'trip-itinerary', TripItineraryViewSet)
router.register(r'trip-approver-groups', ApproverGroupsViewSet)
api_url_patterns = router.urls
