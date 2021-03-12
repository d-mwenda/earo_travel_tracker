"""
All views for the trip app are implemented here.
"""
from smtplib import SMTPRecipientsRefused
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
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
    return_403 = True
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
    return_403 = True
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
        if self.get_object().approval_complete:
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
                self.user_is_approver(traveler, security_level=1) or
                self.user_is_approver(traveler, security_level=2) or
                self.user_is_approver(traveler, security_level=3) or
                traveler.is_managed_by == self.request.user
                )

    def get_context_data(self, **kwargs):
        """
        Add itinerary to context.
        Add approval request form and trip approval status
        """
        context = super().get_context_data(**kwargs)
        context['itinerary'] = self.get_itinerary()
        context['poet_details'] = self.get_poet()
        context['approval_status'] = self.object.get_approval_status()
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

    def send_success_emails(self, trip, approval_request, approver):
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
            'recipient': approver.approver.first_name,
            'host': self.request.get_host(),
            'scheme': self.request.scheme,
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
            [approver.approver.email,],
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
            messages.error(self.request, "We were unable to send emails to one or more recipients. \
                Your approver may not have received the email but they can view the request by \
                checking their pending approval requests on the system. Please contact IT for \
                troubleshooting.")
            print(f"The following error was encountered when sending the emails: {error}")

    def form_valid(self, request, *args, **kwargs):
        """
        Make an approval request by creating an instance of TripApprval.
        """
        trip = self.object
        if not trip.is_owned_by(request.user):
            messages.error(request, "You cannot request approval for a trip you don't own.")
            return self.get(request, *args, **kwargs)

        security_level = trip.get_next_security_level()
        approver = trip.traveler.get_approver(security_level=security_level)
        if approver is None:
            messages.error(request, """We didn't find an approver set for your account.
                        Please contact IT for this to be rectified.""")
            return self.get(request, *args, **kwargs)

        if approver == request.user:
            messages.error(request, "You are set as your own approver for security level"
                f" {security_level}. This is not allowed")
            return self.get(request, *args, **kwargs)

        approval_request = trip.request_approval(security_level, approver)

        # send email to requester and approver
        self.send_success_emails(trip, approval_request, approver)
        messages.success(request, """Your request for approval has been sent.""")
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, trip_id):
        """
        This handles the post method of this view.
        It makes sure that the request for approval is made by the trip owner,
        then it checks the approval submission form for validity and calls appropriate methods to
        handle the request depending on the form validity.
        # TODO maybe extract trip_id from kwargs or request
        """
        self.object = get_object_or_404(self.model, id=trip_id)
        if self.object.is_owned_by(request.user):
            if not self.object.is_valid_for_approval():
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


class TripDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    This class implements the delete view for the Trip model.
    """
    model = Trip
    template_name = "trip/delete_trip.html"
    permission_required = "trip.delete_trip"
    return_403 = True
    pk_url_kwarg = "trip_id"
    extra_context = {
        'page_title': 'Delete Trip'
    }
    success_url = reverse_lazy("u_list_my_trips")

    def get(self, request, *args, **kwargs):
        """
        Ensure that a trip has not been submitted for approval before
        deleting it.
        """
        if self.object.has_began_approval():
            pass
        return super().get(request, *args, **kwargs)


# Trip POET details
class TripPOETCreateView(LoginRequiredMixin, UserPassesTestMixin, TripUtilsMixin, CreateView):
    """
    This class implements the view to add budget details for a trip.

    """
    model = TripPOET
    return_403 = True
    template_name = "trip/add_edit_trip_poet.html"
    fields = ["project", "task"]
    trip = None

    def dispatch(self, request, *args, **kwargs):
        """
        add the associated trip to the request.
        """
        if request.method == "GET":
            trip_id = kwargs.get('trip_id')
            request.session['trip_id'] = trip_id
        else:
            trip_id = request.session.pop("trip_id", None)
        self.trip = get_object_or_404(Trip, id=trip_id)
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        """
        verify that the user creating a POET entry owns the
        associated trip.
        """
        return self.trip.is_owned_by(self.request.user)

    def form_valid(self, form):
        poet = form.save(commit=False)
        poet.trip = self.trip
        poet.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('u_trip_details', kwargs={'trip_id': self.trip.id})


class TripPOETUpdateView(LoginRequiredMixin, PermissionRequiredMixin, TripUtilsMixin, UpdateView):
    """
    Update an instance of Trip POET Details.
    """
    model = TripPOET
    return_403 = True
    template_name = "trip/add_edit_trip_poet.html"
    fields = ["project", "task"]
    pk_url_kwarg = "poet_id"
    permission_required = 'trip.change_trippoet'


class TripPOETDeleteView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Delete an instance of Trip POET Details.
    """
    template_name = ""
    return_403 = True
    permission_required = "trip.delete_trippoet"


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
    trip = None

    def dispatch(self, request, *args, **kwargs):
        """
        add the associated trip to the request.
        """
        if request.method == "GET":
            trip_id = kwargs.get('trip_id')
            request.session['trip_id'] = trip_id
        else:
            trip_id = request.session.pop("trip_id", None)
        self.trip = get_object_or_404(Trip, id=trip_id)
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        """
        verify that the user creating a POET entry owns the
        associated trip.
        """
        return self.trip.is_owned_by(self.request.user)

    def form_valid(self, form):
        trip_leg = form.save(commit=False)
        trip_leg.trip = self.trip
        trip_leg.save()
        return HttpResponseRedirect(self.trip.get_absolute_url())

    # def get_success_url(self):
    #     return reverse_lazy('u_trip_details', kwargs={'trip_id': self.trip_id})


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


class TripItineraryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    This class implements the delete view for the Trip model.
    """
    model = TripItinerary
    permission_required = "trip.delete_tripitinerary"
    return_403 = True
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
    return_403 = True
    permission_denied_message = "It seems like you lack the appropriate permissions to approve "\
                            "this trip. Please contact IT for help."
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
            not trip.is_owned_by(self.request.user)
        )

    def form_valid(self, form):
        """
        If the form is valid, update the Approval model and send email to requester.
        If trip was approved send an approval email, otherwise send a disapproval email.
        """
        approval = form.save(commit=False)
        approval.approval_date = timezone.now().date()
        approval.save()

        # requester will get at least one of 4 possible email messages
        requester_email = approval.trip.traveler.user_account.email
        email_messages = []
        context = {
            'approval_object': approval,
        }

        if approval.trip_is_approved:
            # append success notification message in request
            messages.success(self.request, f"You successfully approved the trip titled \
            {approval.trip.trip_name} as requested by {approval.trip.traveler.user_account.first_name} \
            {approval.trip.traveler.user_account.last_name}")

            # draft success email to requester
            subject = "Trip Approved"
            context["recipient"] = approval.trip.traveler.user_account.first_name
            html_message = render_to_string('emails/approval_confirmation_approved.html', context)
            plain_message = strip_tags(html_message)
            approval_mail = (
                subject,
                plain_message,
                html_message,
                settings.EMAIL_HOST_USER,
                [requester_email,],
            )
            email_messages.append(approval_mail)

            # make next approval request
            next_security_level = approval.trip.get_next_security_level()
            if next_security_level is None: # TODO probably make this a method
                # mark trip as completely approved
                approval.trip.approval_complete = True
                approval.trip.save()

                # TODO draft approval completion email to user
            else:
                approver = approval.trip.traveler.get_approver(security_level=next_security_level)
                # if approver == approval.approver: TODO user cannot be own approver. send error email
                #     approver = obj.trip.traveler.get_approver(security_level=next_security_level)
                if approver is not None:
                    # request approval
                    approval_request = approval.trip.request_approval(next_security_level, approver)
                    approval_request.save()

                    # draft email to requester
                    trip = approval_request.trip
                    subject = f"Trip Approval Requested: {trip.trip_name} beginning on {trip.start_date}"
                    context["trip"] = trip
                    html_message = render_to_string('emails/approval_request_requester.html', context)
                    plain_message = strip_tags(html_message)
                    approval_request_mail = (
                        subject,
                        plain_message,
                        html_message,
                        settings.EMAIL_HOST_USER,
                        [requester_email,],
                        )
                    email_messages.append(approval_request_mail)
                    # draft email to next approver
                    context['recipient'] = approver.approver.first_name
                    context['host'] = self.request.get_host()
                    context['scheme'] = self.request.scheme
                    context['approval_request'] = approval_request
                    subject = f"Trip Approval Requested: {trip.trip_name} beginning on {trip.start_date}"
                    html_message = render_to_string('emails/approval_request_approver.html', context)
                    plain_message = strip_tags(html_message)
                    approver_request_mail = (
                        subject,
                        plain_message,
                        html_message,
                        settings.EMAIL_HOST_USER,
                        [approver.approver.email,],
                        )
                    email_messages.append(approver_request_mail)

                else:
                    # handle no approver
                    subject = "No Approver Set"
                    context['recipient'] = approval.trip.traveler.user_account.first_name
                    context['security_level'] = next_security_level
                    html_message = render_to_string('emails/no_approver.html', context)
                    plain_message = strip_tags(html_message)
                    no_approver_mail = (
                        subject,
                        plain_message,
                        html_message,
                        settings.EMAIL_HOST_USER,
                        [requester_email,],
                        )
                    email_messages.append(no_approver_mail)

        else:
            # append success notification message in request
            messages.success(self.request, f"You successfully declined the trip titled \
            {approval.trip.trip_name} as requested by {approval.trip.traveler.user_account.first_name} \
            {approval.trip.traveler.user_account.last_name}")

            # prepare email to requester
            subject = "Trip Declined"
            html_message = render_to_string('emails/approval_confirmation_declined.html', context)
            plain_message = strip_tags(html_message)
            approval_mail = (
                subject,
                plain_message,
                html_message,
                settings.EMAIL_HOST_USER,
                [requester_email,],
                )
            email_messages.append(approval_mail)

        # send emails
        try:
            send_mass_html_mail(tuple(email_messages))
        except SMTPRecipientsRefused as error:
            pass # TODO handle error better

        return HttpResponseRedirect(self.get_success_url())


class TripApprovalListView(LoginRequiredMixin, ListView):
    """
    This class displays trips whose details have been filled and submitted for approval.
    Depending on the url called, there are dfferent keywords to filter the queryset to return the
    desired queryset.
    """
    # TODO implement permissions here. User passes test of being an approver
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
        # queryset = self.model.objects.filter(
        #     Q(trip__traveler__approver__approver=user) |
        #     Q(trip__traveler__department__trip_approver__approver=user)
        #     )
        queryset = self.model.objects.all()
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
                queryset = queryset.filter(trip_is_approved=False).filter(approver__approver=user)
                self.page_title = "Trips Awaiting Approval"
        self.queryset = queryset
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["page_title"] = self.page_title
        return ctx
