"""
All views for the trip app are implemented here.
"""
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Third party imports
from rest_framework import viewsets
# Earo_travel_tracker imports
from .models import Trips, TripTravelerDependants, TripExpenses, TripApproval, TripItinerary,\
    ApprovalGroups
from .serializers import TripSerializer, TripTravelerDependantsSerializer, TripExpensesSerializer,\
    TripApprovalSerializer, TripItinerarySerializer, ApprovalGroupsSerializer
from .forms import TripForm


# API endpoint views
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


# Non-API views
# Trip
class TripCreateView(LoginRequiredMixin, CreateView):
    """
    This class implements the create view for the Trip model.
    """
    # Todo. Trip cannot begin in the past. This might have to be implemented in the model save method or form validation. It should also be a test case.
    model = Trips
    form_class = TripForm
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'New Trip'
    }


class TripUpdateView(LoginRequiredMixin, UpdateView):
    """
    This class implements the update view for the Trip model.
    """
    model = Trips
    form_class = TripForm
    pk_url_kwarg = 'trip_id'
    context_object_name = 'trip'
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'Edit Trip'
    }


class TripDetailView(LoginRequiredMixin, DetailView):
    """
    This class implements the details view for the Trip model.
    """
    model = Trips
    itinerary_model = TripItinerary
    pk_url_kwarg = 'trip_id'
    context_object_name = 'trip'
    template_name = 'trip/trip_details.html'
    extra_context = {
        'page_title': 'Trip Details',
    }

    def get_itinerary(self):
        """
        Get itinerary legs associated with a trip.
        """
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.itinerary_model.objects.filter(trip=pk)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add itinerary to context.
        """
        context = super(TripDetailView, self).get_context_data(**kwargs)
        context['itinerary'] = self.get_itinerary()
        return context


class TripListView(LoginRequiredMixin, ListView):
    """
    This class implements the listing view for the Trip model.
    """
    # Todo: implement time-based filters for ongoing and upcoming trips
    model = Trips
    context_object_name = 'trips'
    template_name = 'trip/list_trips.html'
    extra_context = {
        'page_title': 'Trips'
    }


class TripDeleteView(LoginRequiredMixin, DeleteView):
    """
    This class implements the delete view for the Trip model.
    """
    model = Trips
    template_name = 'trip/delete_trip.html'
    extra_context = {
        'page_title': 'Delete Trip'
    }


# Trip Itinerary
class TripItineraryCreateView(LoginRequiredMixin, CreateView):
    """
    This class implements the create view for the TripItinerary model.
    """
    # Todo. Trip Itinerary start and end dates must be bound by trip start and end dates.
    # Todo. implement form class with place holders and no Leg status
    model = TripItinerary
    fields = '__all__'
    template_name = 'trip/add_edit_trip_itinerary.html'
    extra_context = {
        'page_title': 'Trip Itinerary',
        'section_title': 'Add a Leg'
    }
    # success_url = reverse_lazy('u_trip_details', kwargs={'trip_id': 1})


class TripItineraryUpdateView(LoginRequiredMixin, UpdateView):
    """
    This class implements the update view for the TripItinerary model.
    """
    model = TripItinerary
    fields = "__all__"
    pk_url_kwarg = 'leg_id'
    template_name = 'trip/add_edit_trip_itinerary.html'
    extra_context = {
        'page_title': 'Edit Trip Itinerary'
    }

class TripItineraryListView(LoginRequiredMixin, ListView):
    """
    This class implements the listing view for the TripItinerary model.
    """
    # Todo: implement time-based filters for ongoing and upcoming trips
    model = TripItinerary
    context_object_name = 'trip_itinerary'
    template_name = 'trip/list_trip_itinerary.html'
    extra_context = {
        'page_title': 'Trip Itinerary'
    }


class TripItineraryDeleteView(LoginRequiredMixin, DeleteView):
    """
    This class implements the delete view for the Trip model.
    """
    model = TripItinerary
    template_name = 'trip/delete_trip_leg.html'
    extra_context = {
        'page_title': 'Delete Leg'
    }
