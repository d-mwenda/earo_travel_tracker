"""
This file provides all view functionality for the traveler app.
"""
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
# Third party apps imports
from rest_framework import viewsets
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin, PermissionListMixin
# Earo_travel_tracker imports
from .models import (
    Approver, CountrySecurityLevel, Departments, TravelerProfile, ApprovalDelegation
)
from .serializers import TravelerProfileSerializer, DepartmentSerializer
from .forms import TravelerBioForm, ApprovalDelegationForm, ApprovalDelegationRevocationForm

USER_MODEL = get_user_model()
# Rest API Views
class TravelerViewSet(viewsets.ModelViewSet):
    """
    This class provides the requisite functionality to manipulate traveler details.
    """
    queryset = TravelerProfile.objects.all()
    serializer_class = TravelerProfileSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    This class implements the view functionality for departments
    """
    queryset = Departments.objects.all()
    serializer_class = DepartmentSerializer


# classes below are Non-API views
# Approver
class ApproverCreateView(LoginRequiredMixin,CreateView):
    """
    Add Users as approvers. This enables easier permission management for approval views.
    TODO implement permissions
    """
    permission_required = 'traveler.add_approver'
    model = Approver
    fields = ['user', 'security_level']
    template_name = 'traveler/add_edit_approver.html'
    extra_context = {
        'page_title': 'Add Approver'
    }

    def get_success_url(self):
        return reverse_lazy('list_approvers')


class ApproverDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Show the details of a single country.
    """
    permission_required = "traveler.view_approver"
    model = Approver
    template_name = "traveler/approver_detail.html"
    context_object_name = "approver"
    pk_url_kwarg = "approver_id"


class ApproverListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Show the details of a single country.
    """
    permission_required = "traveler.view_approver"
    return_403 = True
    model = Approver
    template_name = "traveler/list_approvers.html"
    context_object_name = "approvers"


class ApproverUpdateView(LoginRequiredMixin, PermissionListMixin, UpdateView):
    """
    Update the details of a single country.
    """
    permission_required = "traveler.change_approver"
    return_403 = True
    model = Approver
    fields = ['user', 'security_level', 'is_active']
    template_name = "traveler/add_edit_approver.html"
    pk_url_kwarg = "approver_id"
    context_object_name = "approver"
    extra_context = {
        'page_title': 'Edit Approver'
    }


class ApproverDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete entry of a single country.
    """
    model = Approver
    template_name = "traveler/delete_approver.html"
    pk_url_kwarg = "approver_id"
    context_object_name = "approver_id"


# Country Security Level
class CountrySecurityLevelCreateView(LoginRequiredMixin, CreateView):
    """
    Add countries and their appropriate security levels
    TODO implement permissions
    """
    permission_required = 'traveler.add_countrysecuritylevel'
    model = CountrySecurityLevel
    fields = ['country', 'security_level', 'security_level_3_approver']
    template_name = 'traveler/add_edit_country.html'


class CountrySecurityLevelDetailView(LoginRequiredMixin, DetailView):
    """
    Show the details of a single country.
    """
    model = CountrySecurityLevel
    template_name = "traveler/country_detail.html"
    pk_url_kwarg = "country_id"
    context_object_name = "country"


class CountrySecurityLevelListView(LoginRequiredMixin, ListView):
    """
    Show the details of a single country.
    """
    model = CountrySecurityLevel
    template_name = "traveler/list_countries.html"
    context_object_name = "countries"


class CountrySecurityLevelUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update the details of a single country.
    """
    model = CountrySecurityLevel
    fields = ['country', 'security_level', 'security_level_3_approver']
    template_name = "traveler/add_edit_country.html"
    pk_url_kwarg = "country_id"
    context_object_name = "country"


class CountrySecurityLevelDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete entry of a single country.
    """
    model = CountrySecurityLevel
    template_name = "traveler/delete_country.html"


# Department
class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Creating new departments.
    """
    accept_global_perms = True
    return_403 = True
    permission_required = 'traveler.add_departmentsmodel'
    permission_object = None
    model = Departments
    fields = ['department', 'description', 'security_level_1_approver', 'security_level_2_approver']
    template_name = 'traveler/add_edit_department.html'
    extra_context = {
        'page_title': 'Add Department'
    }


class DepartmentListView(LoginRequiredMixin, ListView):
    """
    View all departments.
    """
    model = Departments
    context_object_name = 'departments'
    template_name = 'traveler/list_departments.html'
    extra_context = {
        'page_title': 'All Departments'
    }


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    """
    View all departments.
    """
    model = Departments
    context_object_name = 'department'
    pk_url_kwarg = 'department_id'
    template_name = 'traveler/department_profile.html'
    extra_context = {
        'page_title': 'Department Profile'
    }


class DepartmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View all departments.
    """
    return_403 = True
    model = Departments
    fields = ['department', 'description', 'security_level_1_approver', 'security_level_2_approver']
    pk_url_kwarg = 'department_id'
    context_object_name = 'department'
    permission_required = 'traveler.change_departmentsmodel'
    template_name = 'traveler/add_edit_department.html'
    # success_url = reverse_lazy('u_department_details', kwargs={'department_id': 'department.id'})
    extra_context = {
        'page_title': 'Edit department'
    }


class DepartmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View all departments.
    """
    model = Departments
    permission_required = "traveler.delete_department"
    return_403 = True


# Travelers
class TravelerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Add new travelers.
    """
    model = TravelerProfile
    form_class = TravelerBioForm
    permission_required = 'traveler.create_travelerdetails'
    return_403 = True
    permission_object = None
    template_name = 'traveler/add_edit_traveler.html'
    extra_context = {
        'page_title': 'Add Traveler'
    }


class TravelerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    View all registered travelers.
    """
    model = TravelerProfile
    context_object_name = 'travelers'
    permission_required = 'traveler.view_travelerdetails'
    return_403 = True
    template_name = 'traveler/list_travelers.html'
    extra_context = {
        'page_title': 'All Travelers'
    }


class TravelerDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    View a travelers profile.
    """
    model = TravelerProfile
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    permission_required = 'traveler.view_travelerdetails'
    return_403 = True
    template_name = 'traveler/traveler_profile.html'
    extra_context = {
        'page_title': 'Traveler Profile'
    }


class TravelerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View a travelers profile.
    """
    model = TravelerProfile
    form_class = TravelerBioForm
    permission_required = 'traveler.change_travelerdetails'
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    template_name = 'traveler/add_edit_traveler.html'
    extra_context = {
        'page_title': 'Edit traveler'
    }


class TravelerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    View a travelers profile.
    """
    model = TravelerProfile
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    permission_required = 'traveler.change_travelerdetails'
    template_name = 'traveler/traveler_profile.html'
    extra_context = {
        'page_title': 'Traveler Profile'
    }

class DelegateApprovalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create an instance of approval delegation"""
    # TODO user cannot delegate to self
    permission_required = "traveler.add_approvaldelegation"
    permission_object = None
    return_403 = True
    form_class = ApprovalDelegationForm
    template_name = "traveler/add_edit_approval_delegation.html"
    active_delegation = None

    def form_valid(self, form):
        approval_delegation = form.save(commit=False)
        user = self.request.user
        approval_delegation.approver_id = user.approver.id
        approval_delegation.save()
        messages.success(self.request, "You have successfully delegated approval")
        return HttpResponseRedirect(reverse_lazy("delegate_approval"))

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        self.get_active_delegation()
        if self.active_delegation is not None:
            ctx['active_delegation'] = self.active_delegation
        return ctx

    def get_active_delegation(self):
        """
        Get existing approval delegation object if any.
        """
        user = self.request.user
        try:
            approver = user.approver
            if approver.active_delegation_exists():
                self.active_delegation = approver.get_active_delegation()
        except USER_MODEL.DoesNotExist:
            pass


class DelegateApprovalUpdateView(UpdateView):
    """Update details on a delegation instance"""
    pass


class RevokeApprovalDelegationView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """View to revoke existing approval"""
    permission_required = "traveler.change_approvaldelegation"
    return_403 = True
    pk_url_kwarg = "delegation_id"
    model = ApprovalDelegation
    form_class = ApprovalDelegationRevocationForm
    context_object_name = "approval_delegation"
    template_name = "traveler/revoke_approval_delegation.html"

    def form_valid(self, form):
        revocation = form.save(commit=False)
        revocation.active = False
        revocation.save()
        messages.success(self.request, "You have successfully revoked delegation of approval")
        return HttpResponseRedirect(reverse_lazy("delegate_approval"))


class DelegateApprovalListView(ListView):
    """
    See a list of all active delegations.
    Non-admin users only see their own delegations
    """
    pass


class DelegateApprovalDetailView(DetailView):
    """See details of an approval delegation"""
    pass
