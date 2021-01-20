"""
All url mappings for the trip app are defined here
"""
from django.urls import path
# Third party app imports
from rest_framework import routers
# Earo_travel_tracker imports
from .views import (
    TripViewSet, TripTravelerDependantsViewSet, TripApprovalViewSet, TripItineraryViewSet,
    TripCreateView, TripDetailView, TripUpdateView, TripDeleteView,
    TripListView, TripPOETCreateView, TripPOETUpdateView ,TripItineraryListView,
    TripItineraryCreateView, TripItineraryUpdateView, TripItineraryDeleteView, ApproveTripView,
    TripApprovalListView,
    )

router = routers.SimpleRouter()
router.register(r'trips', TripViewSet)
router.register(r'trip-traveler-dependants', TripTravelerDependantsViewSet)
router.register(r'trip-approval', TripApprovalViewSet)
router.register(r'trip-itinerary', TripItineraryViewSet)
api_url_patterns = router.urls


urlpatterns = [
    # trips
    path('new-trip', TripCreateView.as_view(), name='u_create_trip'),
    path('list-trips/ongoing', TripApprovalListView.as_view(),  {'filter_by': 'ongoing'},
    name='u_list_ongoing_trips'),
    path('list-trips/upcoming', TripApprovalListView.as_view(), {'filter_by': 'upcoming'},
        name='u_list_upcoming_trips'),
    path('list-trips/my-trips', TripListView.as_view(), name='u_list_my_trips'),
    path('list-trips/awaiting-approval', TripApprovalListView.as_view(),
        {'filter_by': 'awaiting_approval'}, name='u_list_awaiting_approval_trips'),
    path('update-trip/trip=<trip_id>', TripUpdateView.as_view(), name='u_update_trip'),
    path('trip-details/trip=<trip_id>', TripDetailView.as_view(), name='u_trip_details'),
    path('delete-trip', TripDeleteView.as_view(), name='u_delete_trip'),
    # trip poet
    path('trip-poet/add/trip=<trip_id>', TripPOETCreateView.as_view(), name='add_poet'),
    path('trip-poet/update/trip=<trip_id>', TripPOETUpdateView.as_view(), name='update_poet'),
    # trip itinerary
    path('trip-itinerary/new-leg/trip=<trip_id>', TripItineraryCreateView.as_view(),
        name='u_create_trip_itinerary'),
    path('trip-itinerary/trip=<trip_id>', TripItineraryListView.as_view(),
        name='u_list_trip_itinerary'),
    path('trip-itinerary/trip-leg=<leg_id>', TripItineraryUpdateView.as_view(),
        name='u_update_trip_itinerary'),
    path('trip-itinerary/trip=<trip_id>', TripItineraryDeleteView.as_view(),
        name='u_delete_trip_itinerary'),
    # traveler dependants
    # trip approval
    path('trip-approval/approval_request=<approval_id>', ApproveTripView.as_view(),
        name='u_approve_trip'),
]
