"""
This file provides all view functionality for the traveler app.
"""
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Third party apps imports
from rest_framework import viewsets
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Earo_travel_tracker imports
from .models import TravelerDetails, DepartmentsModel
from .serializers import TravelerDetailsSerializer, DepartmentSerializer
from .forms import TravelerBioForm


# Rest API Views
class TravelerViewSet(viewsets.ModelViewSet):
    """
    This class provides the requisite functionality to manipulate traveler details.
    """
    queryset = TravelerDetails.objects.all()
    serializer_class = TravelerDetailsSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    This class implements the view functionality for departments
    """
    queryset = DepartmentsModel.objects.all()
    serializer_class = DepartmentSerializer


# classes below are Non-API views
# Department
class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Creating new departments.
    """
    accept_global_perms = True
    return_403 = True
    permission_required = 'traveler.add_departmentsmodel'
    permission_object = None
    model = DepartmentsModel
    fields = ['department', 'description', 'trip_approver',]
    template_name = 'traveler/add_edit_department.html'
    extra_context = {
        'page_title': 'Add Department'
    }


class DepartmentListView(LoginRequiredMixin, ListView):
    """
    View all departments.
    """
    model = DepartmentsModel
    context_object_name = 'departments'
    template_name = 'traveler/list_departments.html'
    extra_context = {
        'page_title': 'All Departments'
    }


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    """
    View all departments.
    """
    model = DepartmentsModel
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
    model = DepartmentsModel
    fields = ['department', 'description', 'trip_approver',]
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
    model = DepartmentsModel


# Travelers
class TravelerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Add new travelers.
    """
    model = TravelerDetails
    form_class = TravelerBioForm
    permission_required = 'traveler.create_travelerdetails'
    permission_object = None
    template_name = 'traveler/add_edit_traveler.html'
    extra_context = {
        'page_title': 'Add Traveler'
    }


class TravelerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    View all registered travelers.
    """
    model = TravelerDetails
    context_object_name = 'travelers'
    permission_required = 'traveler.view_travelerdetails'
    template_name = 'traveler/list_travelers.html'
    extra_context = {
        'page_title': 'All Travelers'
    }


class TravelerDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    View a travelers profile.
    """
    model = TravelerDetails
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    permission_required = 'traveler.view_travelerdetails'
    template_name = 'traveler/traveler_profile.html'
    extra_context = {
        'page_title': 'Traveler Profile'
    }


class TravelerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View a travelers profile.
    """
    model = TravelerDetails
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
    model = TravelerDetails
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    permission_required = 'traveler.change_travelerdetails'
    template_name = 'traveler/traveler_profile.html'
    extra_context = {
        'page_title': 'Traveler Profile'
    }
