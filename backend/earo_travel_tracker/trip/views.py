"""
All views for the trip app are implemented here.
"""
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect

# Third party imports
from rest_framework import viewsets
# Earo_travel_tracker imports
from traveler.models import TravelerDetails
from .models import (
    Trips, TripTravelerDependants, TripExpenses, TripApproval, TripItinerary, ApprovalGroups
    )
from .serializers import (
    TripSerializer, TripItinerarySerializer, TripExpensesSerializer, TripApprovalSerializer,
    TripTravelerDependantsSerializer, ApprovalGroupsSerializer
    )
from .forms import TripForm, ApprovalRequestForm, TripApprovalForm, TripItineraryForm
from .utils import UserOwnsTripMixin


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
    object = None
    form_class = TripForm
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'New Trip'
    }

    def form_valid(self, form, *args, **kwargs):
        self.object = form.save(commit=False)
        self.object.traveler = TravelerDetails.objects.get(user_account=self.request.user)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TripUpdateView(LoginRequiredMixin, UpdateView):
    """
    This class implements the update view for the Trip model.
    """
    # TODO. approved trips cannot be modified, otherwise they require reapproval.
    model = Trips
    form_class = TripForm
    pk_url_kwarg = 'trip_id'
    context_object_name = 'trip'
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'Edit Trip'
    }


class TripDetailView(LoginRequiredMixin, UserOwnsTripMixin, DetailView):
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
        'approval_request_success_message': None,
        'approval_request_error_message': None,
    }
    form_class = ApprovalRequestForm
    approval_status = None

    def get_context_data(self, **kwargs):
        """
        Add itinerary to context.
        Add approval request form and trip approval status
        """
        context = super().get_context_data(**kwargs)
        context['itinerary'] = self.get_itinerary()
        context['approval_status'] = self.get_approval_status()
        if context['approval_status'] == 'Not requested':
            context['form'] = self.form_class
        return context

    def get_itinerary(self):
        """
        Get itinerary legs associated with a trip.
        """
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.itinerary_model.objects.filter(trip=pk)
        return queryset

    def get_approval_status(self):
        """
        Check if a trip is approved. This helps in rendering the template
        so that appropriate buttons and messages are displayed.
        """
        pk = self.kwargs.get(self.pk_url_kwarg)
        status = None
        try:
            queryset = TripApproval.objects.get(trip=self.get_object())
            if queryset.trip_is_approved:
                status = 'Approved'
            else:
                status = 'Unapproved'
        except ObjectDoesNotExist:
            status = 'Not requested'
        return status

    def get_success_url(self, trip_id):
        """
        Return the detail_view of the object after trip approval has been requested.
        This method is also called whenever an error is encountered during processing
        the trip approval. In such instances, the approval_request_error_message in
        extra context is first set before this method is called.
        """
        return reverse_lazy('u_trip_details',
                            kwargs={'trip_id': trip_id})

    def get_approver(self, request, trip_id):
        """
        Get the approver for the logged on user or return an error is the user has no
        approver set.
        """
        try:
            return  TravelerDetails.objects.get(user_account=request.user).approver
        except ObjectDoesNotExist:
            self.extra_context['approval_request_error_message'] = """We didn't find an
                                    approver set for your account. Please contact IT for
                                    this to be fixed then thereafter you can retry requesting
                                    for approval."""
            return self.get_success_url(trip_id)

    def reset_approval_request_messages(self):
        """
        This method resets the approval_request_messages in the context so that they don't
        persist between requests.
        """
        self.extra_context['approval_request_success_message'] = None
        self.extra_context['approval_request_error_message'] = None
        return

    def form_valid(self, request, trip_id):
        """
        Make an approval request by creating an instance of TripApprval
        """
        approver=self.get_approver(request, trip_id)
        if approver:
            try:
                approval_request = TripApproval(trip=self.model.objects.get(id=trip_id),
                                                approver=approver)
                approval_request.save()
                self.extra_context['approval_request_success_message'] = """Your request for approval
                                                                        has been sent."""
                # TODO: send email to approver and requester.
                print('requesting approval')
            except IntegrityError:
                self.extra_context['approval_request_error_message'] = """An approval request for this
                                        trip was already sent earlier. You can only request for 
                                        approval once. If you wish to send a reminder, consider sending
                                        an email to your approver."""
                print('at integrity constraint')
        else:
            self.extra_context['approval_request_error_message'] = """We didn't find an approver set
                                    for your account. Please contact IT for this to be rectified."""
            print("at no approver set")
        return HttpResponseRedirect(self.get_success_url(trip_id))

    def post(self, request, trip_id):
        """
        This handles the post method of this view.
        It makes sure that the request for approval is made by the trip owner,
        then it checks the approval submission form for validity and calls appropriate methods to
        handle the request depending on the form validity.
        """
        self.reset_approval_request_messages()
        if self.user_owns_trip(trip_id):
            form = self.form_class(request.POST)
            if form.is_valid():
                return self.form_valid(request, trip_id)
            else:
                self.extra_context['approval_request_error_message'] = "Form tampering suspected."
                return HttpResponseRedirect(self.get_success_url(trip_id))
        else:
            self.extra_context['approval_request_error_message'] = """You cannot submit a request
                                                                 for a trip you don't own."""
            return HttpResponseRedirect(self.get_success_url(trip_id))


class TripListView(LoginRequiredMixin, ListView):
    """
    This class implements the listing view for the Trip model.
    """
    # TODO: implement time-based filters for ongoing and upcoming trips
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
class TripItineraryCreateView(LoginRequiredMixin, UserOwnsTripMixin, CreateView):
    """
    This class implements the create view for the TripItinerary model.
    """
    # TODO. Trip Itinerary start and end dates must be bound by trip start and end dates.
    # TODO. implement form class with place holders and no Leg status
    model = TripItinerary
    form_class = TripItineraryForm
    template_name = 'trip/add_edit_trip_itinerary.html'
    extra_context = {
        'page_title': 'Trip Itinerary',
        'section_title': 'Add a Leg'
    }
    # success_url = reverse_lazy('u_trip_details', kwargs={'trip_id': 1})

    def get(self, request, *args, **kwargs):
        """
        add trip_id to request for security and prevent user tampering.
        Use the trip_id from the request in the post
        """
        # TODO first check that trip exists
        # TODO verify that user owns trip
        request.session['trip'] = kwargs.get('trip_id')
        return super().get(request)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        trip_id = request.session.get('trip')
        if form.is_valid():
            return self.form_valid(form, trip_id)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, trip_id):
        trip_leg = form.save(commit=False)
        trip_leg.trip = Trips.objects.get(id=trip_id)
        trip_leg.save()
        return HttpResponseRedirect(self.get_success_url(trip_id))
    
    def get_success_url(self, trip_id):
        return reverse_lazy('u_trip_details', kwargs={'trip_id': trip_id})


class TripItineraryUpdateView(LoginRequiredMixin, UpdateView):
    """
    This class implements the update view for the TripItinerary model.
    """
    model = TripItinerary
    form_class = TripItineraryForm
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


# Trip approvals
class ApproveTripView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    This class creates handles approving a trip.
    """
    model = TripApproval
    form_class = TripApprovalForm
    permission_denied_message = """It seems like you lack the appropriate permissions to approve.
                                Please contact IT for help"""
    success_url = reverse_lazy('u_list_awaiting_approval_trips')
    pk_url_kwarg = 'approval_id'
    template_name = 'trip/approve_trip.html'
    extra_context = {
        'page_title': 'Trips'
    }

    def user_is_approver(self):
        """
        Confirm that the logged on user is the approver for the request.
        """
        print(self.get_object())
        return bool(self.request.user == self.get_object().approver)

    def get_test_func(self):
        return self.user_is_approver


class TripApprovalListView(LoginRequiredMixin, ListView):
    """
    This class displays trips whose details have been filled and submitted for approval.
    Depending on the url called, there are dfferent keywords to filter the queryset to return the
    desired queryset.
    """
    model = TripApproval
    context_object_name = 'trips'
    template_name = 'trip/list_trips.html'
    extra_context = {
        'page_title': 'Trips'
    }

    def get(self, request, *args, filter_by=None, **kwargs):
        """
        This method filters the queryset accordingly, depending on the url that calls the view.
        """
        if filter_by:
            if filter_by == "upcoming":
                queryset = self.model.objects.filter(trip__start_date__gt = timezone.now().date())
            elif filter_by == "ongoing":
                queryset = self.model.objects.filter(trip__start_date__lte = timezone.now().date())
                queryset = queryset.filter(trip__end_date__gte = timezone.now().date())
            elif filter_by== 'awaiting_approval':
                queryset = self.model.objects.filter(trip_is_approved=False)
        self.queryset = queryset
        return super().get(request, *args, **kwargs)
