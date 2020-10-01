"""
All url mappings for the trip app are defined here
"""
from django.urls import path
# Third party app imports
from rest_framework import routers
# Earo_travel_tracker imports
from .views import TripViewSet, TripTravelerDependantsViewSet, TripExpensesViewSet,\
    TripApprovalViewSet, TripItineraryViewSet, ApproverGroupsViewSet, TripCreateView,\
    TripDetailView, TripUpdateView, TripDeleteView, TripListView, TripItineraryListView,\
    TripItineraryCreateView, TripItineraryUpdateView, TripItineraryDeleteView


router = routers.SimpleRouter()
router.register(r'trips', TripViewSet)
router.register(r'trip-traveler-dependants', TripTravelerDependantsViewSet)
router.register(r'trip-expenses', TripExpensesViewSet)
router.register(r'trip-approval', TripApprovalViewSet)
router.register(r'trip-itinerary', TripItineraryViewSet)
router.register(r'trip-approver-groups', ApproverGroupsViewSet)
api_url_patterns = router.urls


urlpatterns = [
    # trips
    path('new-trip', TripCreateView.as_view(), name='u_create_trip'),
    path('list-trips/ongoing', TripListView.as_view(), name='u_list_ongoing_trips'),
    path('list-trips/upcoming', TripListView.as_view(), name='u_list_upcoming_trips'),
    path('update-trip/trip=<trip_id>', TripUpdateView.as_view(), name='u_update_trip'),
    path('trip-details/trip=<trip_id>', TripDetailView.as_view(), name='u_trip_details'),
    path('delete-trip', TripDeleteView.as_view(), name='u_delete_trip'),
    # trip itinerary
    # path('trip-itinerary/trip=<trip_id>/new-leg', TripItineraryCreateView.as_view(), name='u_create_trip_itinerary'),
    path('trip-itinerary/new-leg', TripItineraryCreateView.as_view(),
        name='u_create_trip_itinerary'),
    path('trip-itinerary/trip=<trip_id>', TripItineraryListView.as_view(),
        name='u_list_trip_itinerary'),
    path('trip-itinerary/trip-leg=<leg_id>', TripItineraryUpdateView.as_view(),
        name='u_update_trip_itinerary'),
    path('trip-itinerary/trip=<trip_id>', TripItineraryDeleteView.as_view(),
        name='u_delete_trip_itinerary'),
    # traveler dependants
    path('trip-traveler-dependants', TripTravelerDependantsViewSet),
    path('trip-expenses', TripExpensesViewSet),
    # trip approval
    path('trip-approval', TripApprovalViewSet),
    # trip approver groups
    path('trip-approver-groups', ApproverGroupsViewSet),
]
