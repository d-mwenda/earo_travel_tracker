"""
All views for the trip app are implemented here.
"""
from smtplib import SMTPRecipientsRefused
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.shortcuts import get_object_or_404

# Third party imports
from rest_framework import viewsets
from guardian.mixins import PermissionRequiredMixin, PermissionListMixin, LoginRequiredMixin
from guardian.shortcuts import get_perms
# Earo_travel_tracker imports
from traveler.models import TravelerProfile
from utils.emailing import send_mass_html_mail
from .models import (
    Trip, TripTravelerDependants, TripApproval, TripItinerary, TripPOET
    )
from traveler.models import Approver
from .serializers import (
    TripSerializer, TripItinerarySerializer, TripApprovalSerializer,
    TripTravelerDependantsSerializer
    )
from .forms import TripForm, ApprovalRequestForm, TripApprovalForm, TripItineraryForm
from .utils import TripUtilsMixin


# API endpoint views
class TripViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Trips.
    """
    serializer_class = TripSerializer
    queryset = Trip.objects.all()


class TripTravelerDependantsViewSet(viewsets.ModelViewSet):
    """
    This class implements views for the Trips.
    """
    serializer_class = TripTravelerDependantsSerializer
    queryset = TripTravelerDependants.objects.all()


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


# Non-API views
# Trip
class TripCreateView(LoginRequiredMixin, PermissionRequiredMixin,CreateView):
    """
    This class implements the create view for the Trip model.
    Important settings:
    permission_object = None. This ensures that the PermissionRequiredMixin
    doesn't throw an error.
    """
    object = None
    model = Trip
    permission_required = 'trip.add_trip'
    permission_object = None
    accept_global_perms = True
    raise_exception = True
    form_class = TripForm
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'New Trip'
    }

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.traveler = TravelerProfile.objects.get(user_account=self.request.user)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TripUpdateView(LoginRequiredMixin, PermissionRequiredMixin, TripUtilsMixin, UpdateView):
    """
    This class implements the update view for the Trip model.
    """
    object = None
    model = Trip
    form_class = TripForm
    permission_required = 'trip.change_trip'
    raise_exception = True
    pk_url_kwarg = 'trip_id'
    context_object_name = 'trip'
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'Edit Trip'
    }

    def get(self, request, *args, **kwargs):
        """
        Check if the trip being modified is approved. If it's already approved, put a
        message in the request to let the user know the approval will be nullified.
        """
        if self.is_approved_trip():
            messages.warning(request,
                "This trip has already been approved by at least one approver.\
                Modifying the trip details will nullify the approval and the trip needs to \
                be reapproved. If you don't wish to continue, click on the Cancel button."
                )
        return super().get(request, *args, **kwargs)

    # def form_valid(self, form):
        # TODO invalidate the approval.


class TripDetailView(LoginRequiredMixin, UserPassesTestMixin, TripUtilsMixin, DetailView):
    """
    This class implements the details view for the Trip model.
    """
    model = Trip
    return_403 = True
    itinerary_model = TripItinerary
    poet_model = TripPOET
    object = None
    pk_url_kwarg = 'trip_id'
    context_object_name = 'trip'
    template_name = 'trip/trip_details.html'
    extra_context = {
        'page_title': 'Trip Details',
    }
    form_class = ApprovalRequestForm
    approval_status = None

    def test_func(self):
        """
        Check that the user has permission for the instance or is an approver.
        """
        trip = self.get_object()
        traveler = trip.traveler
        user = self.request.user
        return ('view_trip' in get_perms(user, trip) or
                self.user_is_approver(traveler) or
                self.is_line_manager(traveler)
                )

    def get_context_data(self, **kwargs):
        """
        Add itinerary to context.
        Add approval request form and trip approval status
        """
        context = super().get_context_data(**kwargs)
        context['itinerary'] = self.get_itinerary()
        context['poet_details'] = self.get_poet()
        context['approval_status'] = self.get_approval_status()
        if context['approval_status'] == 'Not requested':
            context['form'] = self.form_class
        return context

    def get_itinerary(self):
        """
        Get itinerary legs associated with a trip.
        """
        trip_id = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.itinerary_model.objects.filter(trip=trip_id)
        return queryset

    def get_poet(self):
        """
        Get POET details associated with a trip.
        """
        trip_id = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.poet_model.objects.filter(trip=trip_id)
        return queryset

    def get_success_url(self):
        """
        Return the detail_view of the object after trip approval has been requested.
        This method is also called whenever an error is encountered during processing
        the trip approval. In such instances, the approval_request_error_message in
        extra context is first set before this method is called.
        """
        return reverse_lazy('u_trip_details',
                            kwargs={'trip_id': self.object.id})

    def send_success_emails(self, trip, request, approval_request, approver):
        """
        Send email to the requester and approver once an approval request is made.
        Args:
            trip is an instance of Trips model for which approval is being requested.
            request is the HTTP request in which the request was made.
            approval_request is the instance TripApproval that was created for the
            approval request.
            approver is an instance of settings.USER_MODEL
        """
        subject_line = f"Trip Approval Requested: {trip.trip_name} beginning on {trip.start_date}"
        approver_context = {
            'trip': trip,
            'recipient': approver.first_name,
            'host': request.get_host(),
            'scheme': request.scheme,
            'approval_request': approval_request,
        }

        requester_context = {
            'recipient': trip.traveler.user_account.first_name,
            'trip': trip
        }

        approver_html_message = render_to_string('emails/approval_request_approver.html',
                                                approver_context)
        approver_plain_message = strip_tags(approver_html_message)
        requester_html_message = render_to_string('emails/approval_request_requester.html',
                                                requester_context)
        requester_plain_message = strip_tags(requester_html_message)

        approver_mail = (
            subject_line,
            approver_plain_message,
            approver_html_message,
            settings.EMAIL_HOST_USER,
            [approver.email,],
        )
        requester_mail = (
            subject_line,
            requester_plain_message,
            requester_html_message,
            settings.EMAIL_HOST_USER,
            [trip.traveler.user_account.email,],
            )

        try:
            send_mass_html_mail((approver_mail, requester_mail))
        except SMTPRecipientsRefused as error:
            messages.error(request, "We were unable to send emails to one or more recipients. \
                Your approver may not have received the email but they can view the request by \
                checking their pending approval requests on the system. Please contact IT for \
                troubleshooting.")
            print(f"The following error was encountered when sending the emails: {error}")

    def form_valid(self, request):
        """
        Make an approval request by creating an instance of TripApprval.
        """
        trip = self.object
        if self.user_owns_trip(trip):
            security_level = self.get_next_security_level(trip)
            approver = self.get_approver(trip.traveler, security_level=security_level)
            if approver is not None:
                approval_request = self.request_approval(trip, security_level)

                # send email to requester and approver
                self.send_success_emails(trip, request, approval_request, approver)
                messages.success(request, """Your request for approval has been sent.""")
                print('requesting approval')
            else:
                messages.error(request, """We didn't find an approver set for your account.
                            Please contact IT for this to be rectified."""
                )
                print("at no approver set")
        else:
            messages.error(request, "You cannot request approval for a trip you don't own.")
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, trip_id):
        """
        This handles the post method of this view.
        It makes sure that the request for approval is made by the trip owner,
        then it checks the approval submission form for validity and calls appropriate methods to
        handle the request depending on the form validity.
        """
        self.object = get_object_or_404(self.model, id=trip_id)
        if self.user_owns_trip(self.object):
            if not self.is_valid_for_approval():
                messages.error(request, "This trip cannot be submitted for approval.\
                    It is missing either POET or Itinerary details.")
                self.render_to_response(self.get_context_data(form=form))
            form = self.form_class(request.POST)
            if form.is_valid():
                return self.form_valid(request)
            messages.error(request, "Form tampering suspected.")
            return  self.render_to_response(self.get_context_data(form=form))
        messages.error(request, "You cannot submit a request for a trip you don't own.")
        return HttpResponseRedirect(self.get_success_url())


class TripListView(LoginRequiredMixin, PermissionListMixin, ListView):
    """
    This class implements the listing view for the Trip model.
    """
    model = Trip
    context_object_name = 'trips'
    return_403 = True
    permission_required = 'trip.view_trip'
    template_name = 'trip/view_trips.html'
    extra_context = {
        'page_title': 'My Trips'
    }

    def get_queryset(self, *args, **kwargs):
        """
        Limit the trips to those belonging to the logged on user.
        """
        queryset = super().get_queryset(*args, **kwargs)
        queryset.filter(traveler__user_account=self.request.user)
        return queryset


class TripDeleteView(LoginRequiredMixin, DeleteView):
    """
    This class implements the delete view for the Trip model.
    """
    model = Trip
    template_name = 'trip/delete_trip.html'
    extra_context = {
        'page_title': 'Delete Trip'
    }


# Trip POET details
class TripPOETCreateView(LoginRequiredMixin, TripUtilsMixin, CreateView):
    """
    This class implements the view to add budget details for a trip.

    """
    model = TripPOET
    template_name = "trip/add_edit_trip_poet.html"
    fields = ["project", "task"]
    trip_id = None

    def get(self, request, *args, **kwargs):
        """
        Intercept get request to:
        1. verify that the logged on user owns the trip
        2. add the trip instance to the session data
        """
        trip_id = kwargs.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        if self.user_owns_trip(trip):
            request.session['trip_id'] = trip.id
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        self.trip_id = request.session.get("trip_id")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        poet = form.save(commit=False)
        poet.trip = Trip.objects.get(id=self.trip_id)
        poet.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('u_trip_details', kwargs={'trip_id': self.trip_id})

class TripPOETUpdateView(LoginRequiredMixin, TripUtilsMixin, UpdateView):
    """
    Update an instance of Trip POET Details.
    """
    model = TripPOET
    template_name = "trip/add_edit_trip_poet.html"
    fields = ["project", "task"]
    trip_id = None
    pk_url_kwarg = "poet_id"

    def get(self, request, *args, **kwargs):
        """
        Intercept get request to:
        1. verify that the logged on user owns the trip
        2. add the trip instance to the session data
        """
        trip_id = kwargs.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        if self.user_owns_trip(trip):
            request.session['trip_id'] = trip.id
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        self.trip_id = request.session.get("trip_id")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('u_trip_details', kwargs={'trip_id': self.trip_id})


class TripPOETDeleteView(LoginRequiredMixin, UpdateView):
    """
    Delete an instance of Trip POET Details.
    """
    template_name = ""


# Trip Itinerary
class TripItineraryCreateView(LoginRequiredMixin, TripUtilsMixin, CreateView):
    """
    This class implements the create view for the TripItinerary model.
    """
    model = TripItinerary
    form_class = TripItineraryForm
    template_name = 'trip/add_edit_trip_itinerary.html'
    extra_context = {
        'page_title': 'Trip Itinerary',
        'section_title': 'Add a Leg'
    }
    trip_id = None

    def get(self, request, *args, **kwargs):
        """
        add trip_id to request for security and prevent user tampering.
        Use the trip_id from the request in the post
        """
        trip_id = kwargs.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        if self.user_owns_trip(trip):
            request.session['trip'] = trip.id
            return super().get(request)
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        self.trip_id = request.session.get('trip')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        trip_leg = form.save(commit=False)
        trip_leg.trip = Trip.objects.get(id=self.trip_id)
        trip_leg.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('u_trip_details', kwargs={'trip_id': self.trip_id})


class TripItineraryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    This class implements the update view for the TripItinerary model.
    """
    model = TripItinerary
    form_class = TripItineraryForm
    return_403 = True
    permission_required = 'trip.change_tripitinerary'
    pk_url_kwarg = 'leg_id'
    template_name = 'trip/add_edit_trip_itinerary.html'
    extra_context = {
        'page_title': 'Edit Trip Itinerary'
    }

class TripItineraryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    This class implements the listing view for the TripItinerary model.
    """
    model = TripItinerary
    context_object_name = 'trip_itinerary'
    return_403 = True
    permission_required = 'trip.view_tripitinerary'
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
class ApproveTripView(LoginRequiredMixin, UserPassesTestMixin, TripUtilsMixin, UpdateView):
    """
    This class creates handles approving a trip.
    """
    model = TripApproval
    form_class = TripApprovalForm
    context_object_name = 'trip_approval'
    permission_denied_message = "It seems like you lack the appropriate permissions to approve \
                            this trip. Please contact IT for help."""
    success_url = reverse_lazy('u_list_awaiting_approval_trips')
    pk_url_kwarg = 'approval_id'
    template_name = 'trip/approve_trip.html'
    extra_context = {
        'page_title': 'Trips'
    }

    def test_func(self):
        """
        Check that the logged on user is approver for the trip and
         the trip doesn't below to the same user approving.
        """
        approval = self.get_object()
        trip = approval.trip
        return (
            self.user_is_approver(trip.traveler, security_level=approval.security_level) and
            self.user_owns_trip(trip) is not True
        )

    def form_valid(self, form):
        """
        If the form is valid, update the Approval model and send email to requester.
        If trip was approved send an approval email, otherwise send a disapproval email.
        """
        obj = form.save(commit=False)
        obj.approval_date = timezone.now().date()
        obj.save()
        next_security_level = self.get_next_security_level(obj.trip)
        if next_security_level:
            self.request_approval(obj.trip, next_security_level)
            # TODO send email to approver
        else:
            obj.trip.approval_complete = True
            obj.trip.save()
        messages.success(self.request, f"You successfully approved the trip titled \
            {obj.trip.trip_name} as requested by {obj.trip.traveler.user_account.first_name} \
            {obj.trip.traveler.user_account.last_name}")
        # send email appropriately.
        context = {
                'recipient': obj.trip.traveler.user_account.first_name,
                'approval_object': obj
            }
        if obj.trip_is_approved:
            subject = "Trip Approved"
            html_message = render_to_string('emails/approval_confirmation_approved.html', context)
        else:
            subject = "Trip Declined"
            html_message = render_to_string('emails/approval_confirmation_approved.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [obj.trip.traveler.user_account.email,],
            fail_silently=False,
            html_message=html_message
        )
        return HttpResponseRedirect(self.get_success_url())

class TripApprovalListView(LoginRequiredMixin, ListView):
    """
    This class displays trips whose details have been filled and submitted for approval.
    Depending on the url called, there are dfferent keywords to filter the queryset to return the
    desired queryset.
    """
    # TODO implement permissions here
    model = TripApproval
    context_object_name = 'trips'
    return_403 = True
    template_name = 'trip/list_trips.html'
    page_title = None

    def get(self, request, *args, **kwargs):
        """
        This method filters the queryset accordingly, depending on the url that calls the view.
        """
        filter_by = kwargs['filter_by']
        user = request.user
        queryset = self.model.objects.filter(
            Q(trip__traveler__approver__approver=user) | 
            Q(trip__traveler__department__trip_approver__approver=user)
            )
        if filter_by:
            if filter_by == "upcoming":
                queryset = queryset.filter(trip__start_date__gt = timezone.now().date())
                self.page_title = "Upcoming Trips"
            elif filter_by == "ongoing":
                queryset = queryset.filter(
                                trip__start_date__lte = timezone.now().date(),
                                trip__end_date__gte = timezone.now().date(),
                                trip_is_approved = True
                                )
                self.page_title = "Ongoing Trips"
            elif filter_by== 'awaiting_approval':
                queryset = queryset.filter(trip_is_approved=False)
                self.page_title = "Trips Awaiting Approval"
        self.queryset = queryset
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["page_title"] = self.page_title
        return ctx
