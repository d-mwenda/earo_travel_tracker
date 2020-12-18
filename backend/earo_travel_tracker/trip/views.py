"""
All views for the trip app are implemented here.
"""
from smtplib import SMTPRecipientsRefused
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound, Http404
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages

# Third party imports
from rest_framework import viewsets
from guardian.mixins import PermissionRequiredMixin, PermissionListMixin
from guardian.shortcuts import get_perms
# Earo_travel_tracker imports
from traveler.models import TravelerDetails
from utils.emailing import send_mass_html_mail
from .models import (
    Trips, TripTravelerDependants, TripExpenses, TripApproval, TripItinerary, ApprovalGroups
    )
from .serializers import (
    TripSerializer, TripItinerarySerializer, TripExpensesSerializer, TripApprovalSerializer,
    TripTravelerDependantsSerializer, ApprovalGroupsSerializer
    )
from .forms import TripForm, ApprovalRequestForm, TripApprovalForm, TripItineraryForm
from .utils import TripUtilsMixin


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
class TripCreateView(DjangoPermissionRequiredMixin, CreateView):
    """
    This class implements the create view for the Trip model.
    """
    model = Trips
    permission_required = 'trip.add_trips'
    raise_exception = True
    form_class = TripForm
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'New Trip'
    }

    def form_valid(self, form):
        trip = form.save(commit=False)
        trip.traveler = TravelerDetails.objects.get(user_account=self.request.user)
        trip.save()
        return HttpResponseRedirect(self.get_success_url())


class TripUpdateView(PermissionRequiredMixin, UpdateView):
    """
    This class implements the update view for the Trip model.
    """
    # TODO. approved trips cannot be modified, otherwise they require reapproval.
    model = Trips
    form_class = TripForm
    permission_required = 'trip.change_trips'
    raise_exception = True
    pk_url_kwarg = 'trip_id'
    context_object_name = 'trip'
    template_name = 'trip/add_edit_trip.html'
    extra_context = {
        'page_title': 'Edit Trip'
    }


class TripDetailView(LoginRequiredMixin, UserPassesTestMixin, TripUtilsMixin, DetailView):
    """
    This class implements the details view for the Trip model.
    """
    # TODO: check that user is approver or has perm in order to view this view
    model = Trips
    return_403 = True
    itinerary_model = TripItinerary
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
        TODO add line manager and SMT to allowed. SMT can be granted perms via group
        """
        trip = self.get_object()
        user = self.request.user
        return 'view_trips' in get_perms(user, trip) or self.user_is_approver(trip.traveler)

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
        subject_line = f"""Trip Approval Requested: {trip.trip_name} beginning on {trip.start_date}"""
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

        approver_html_message = render_to_string('emails/approval_request_approver.html', approver_context)
        approver_plain_message = strip_tags(approver_html_message)
        requester_html_message = render_to_string('emails/approval_request_requester.html', requester_context)
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

    def form_valid(self, request, trip_id):
        """
        Make an approval request by creating an instance of TripApprval.
        """
        trip = self.model.objects.get(id=trip_id)
        if self.user_owns_trip(trip):
            approver = self.get_approver(self.get_object().traveler)
            if approver is not None:
                try:
                    approval_request = TripApproval(trip=trip)
                    approval_request.save()
                    messages.success(request, """Your request for approval has been sent.""")
                    print('requesting approval')
                    # send email to requester and approver
                    self.send_success_emails(trip, request, approval_request, approver)

                except IntegrityError:
                    messages.error(
                        request,
                        """An approval request for this trip was already sent earlier.
                        You can only request for approval once. If you wish to send a reminder,
                        consider sending an email to your approver."""
                    )
                    print('at integrity constraint')
            else:
                messages.error(request, """We didn't find an approver set for your account.
                            Please contact IT for this to be rectified."""
                )
                print("at no approver set")
        else:
            messages.error(request, "You cannot request approval for a trip you don't own.")
        return HttpResponseRedirect(self.get_success_url(trip_id))

    def post(self, request, trip_id):
        """
        This handles the post method of this view.
        It makes sure that the request for approval is made by the trip owner,
        then it checks the approval submission form for validity and calls appropriate methods to
        handle the request depending on the form validity.
        """
        trip = self.get_object()
        if self.user_owns_trip(trip):
            form = self.form_class(request.POST)
            if form.is_valid():
                return self.form_valid(request, trip_id)
            else:
                messages.error(request, "Form tampering suspected.")
                return  self.render_to_response(self.get_context_data(form=form))

        else:
            self.extra_context['approval_request_error_message'] = """You cannot submit a request
                                                                 for a trip you don't own."""
            return HttpResponseRedirect(self.get_success_url(trip_id))

    def get(self, request, *args, **kwargs):
        return super().get(self, request, *args, **kwargs)


class TripListView(PermissionListMixin, ListView):
    """
    This class implements the listing view for the Trip model.
    """
    model = Trips
    context_object_name = 'trips'
    return_403 = True
    permission_required = 'trip.view_trips'
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
    model = Trips
    template_name = 'trip/delete_trip.html'
    extra_context = {
        'page_title': 'Delete Trip'
    }


# Trip Itinerary
class TripItineraryCreateView(LoginRequiredMixin, TripUtilsMixin, CreateView):
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

    def get_trip(self, trip_id):
        """
        Get the trip for which an itinerary leg is to be created.
        """
        try:
            return Trips.objects.get(id=trip_id)
        except Trips.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        """
        add trip_id to request for security and prevent user tampering.
        Use the trip_id from the request in the post
        """
        trip_id = kwargs.get('trip_id')
        trip = self.get_trip(trip_id)
        if self.user_owns_trip(trip):
            return super().get(request)
        else:
            return HttpResponseForbidden()
        request.session['trip'] = kwargs.get(trip_id)
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


class TripItineraryUpdateView(PermissionRequiredMixin, UpdateView):
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

class TripItineraryListView(PermissionRequiredMixin, ListView):
    """
    This class implements the listing view for the TripItinerary model.
    """
    # Todo: implement time-based filters for ongoing and upcoming trips
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
        trip = self.get_object().trip
        return self.user_is_approver(trip.traveler) and self.user_owns_trip(trip) is not True

    def form_valid(self, form):
        """
        If the form is valid, update the Approval model and send email to requester.
        If trip was approved send an approval email, otherwise send a disapproval email.
        """
        obj = form.save(commit=False)
        obj.approval_date = timezone.now().date()
        obj.save()
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

class TripApprovalListView(PermissionRequiredMixin, ListView):
    """
    This class displays trips whose details have been filled and submitted for approval.
    Depending on the url called, there are dfferent keywords to filter the queryset to return the
    desired queryset.
    """
    model = TripApproval
    context_object_name = 'trips'
    return_403 = True
    permission_required = 'trip.view_tripitinerary'
    template_name = 'trip/list_trips.html'
    page_title = None

    def get(self, request, *args, **kwargs):
        """
        This method filters the queryset accordingly, depending on the url that calls the view.
        """
        filter_by = kwargs['filter_by']
        user = request.user
        queryset = self.model.objects.filter(
            Q(trip__traveler__approver=user) |
            Q(trip__traveler__department__trip_approver=user)
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
