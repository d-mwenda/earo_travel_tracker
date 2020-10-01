"""
This file provides all view functionality for the traveler app.
"""
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
# Third party apps imports
from rest_framework import viewsets
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
class DepartmentCreateView(CreateView):
    """
    Creating new departments.
    """
    model = DepartmentsModel
    fields = ['department', 'description']
    template_name = 'traveler/add_edit_department.html'
    extra_context = {
        'page_title': 'Add Department'
    }


class DepartmentListView(ListView):
    """
    View all departments.
    """
    model = DepartmentsModel
    context_object_name = 'departments'
    template_name = 'traveler/list_departments.html'
    extra_context = {
        'page_title': 'All Departments'
    }


class DepartmentDetailView(DetailView):
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


class DepartmentUpdateView(UpdateView):
    """
    View all departments.
    """
    model = DepartmentsModel
    fields = ['department', 'description']
    pk_url_kwarg = 'department_id'
    context_object_name = 'department'
    template_name = 'traveler/add_edit_department.html'
    # success_url = reverse_lazy('u_department_details', kwargs={'department_id': 'department.id'})
    extra_context = {
        'page_title': 'Edit department'
    }


class DepartmentDeleteView(DeleteView):
    """
    View all departments.
    """
    model = DepartmentsModel


# Travelers
class TravelerCreateView(CreateView):
    """
    Add new travelers.
    """
    model = TravelerDetails
    form_class = TravelerBioForm
    template_name = 'traveler/add_edit_traveler.html'
    extra_context = {
        'page_title': 'Add Traveler'
    }


class TravelerListView(ListView):
    """
    View all registered travelers.
    """
    model = TravelerDetails
    context_object_name = 'travelers'
    template_name = 'traveler/list_travelers.html'
    extra_context = {
        'page_title': 'All Travelers'
    }


class TravelerDetailView(DetailView):
    """
    View a travelers profile.
    """
    model = TravelerDetails
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    template_name = 'traveler/traveler_profile.html'
    extra_context = {
        'page_title': 'Traveler Profile'
    }


class TravelerUpdateView(UpdateView):
    """
    View a travelers profile.
    """
    model = TravelerDetails
    form_class = TravelerBioForm
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    template_name = 'traveler/add_edit_traveler.html'
    extra_context = {
        'page_title': 'Edit traveler'
    }


class TravelerDeleteView(DetailView):
    """
    View a travelers profile.
    """
    model = TravelerDetails
    pk_url_kwarg = 'traveler_id'
    context_object_name = 'traveler'
    template_name = 'traveler/traveler_profile.html'
    extra_context = {
        'page_title': 'Traveler Profile'
    }
