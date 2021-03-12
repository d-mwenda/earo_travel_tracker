"""
All url mappings for the traveler app are defined here
"""
from django.urls import path
# Third party app imports
from rest_framework import routers
# Earo_travel_tracker imports
from .views import (
    TravelerViewSet, DepartmentViewSet, DepartmentCreateView, DepartmentListView,
    DepartmentDetailView, DepartmentUpdateView, DepartmentDeleteView, TravelerCreateView,
    TravelerListView, TravelerDetailView, TravelerUpdateView, CountrySecurityLevelCreateView,
    CountrySecurityLevelDeleteView, CountrySecurityLevelDetailView, CountrySecurityLevelUpdateView,
    CountrySecurityLevelListView, ApproverCreateView, ApproverDetailView, ApproverUpdateView,
    ApproverDeleteView, ApproverListView
)


router = routers.SimpleRouter()
router.register(r'traveler', TravelerViewSet)
router.register(r'departments', DepartmentViewSet)
api_url_patterns = router.urls

urlpatterns = [
    # Department views urls
    path('new-department', DepartmentCreateView.as_view(), name='u_create_department'),
    path('list-departments', DepartmentListView.as_view(), name='u_list_departments'),
    path('department-details/department=<department_id>',
        DepartmentDetailView.as_view(), name='u_department_details'),
    path('edit-department/department=<department_id>',
        DepartmentUpdateView.as_view(), name='u_edit_department'),
    path('delete-department', DepartmentDeleteView.as_view(), name='u_delete_department'),
    # Traveler views urls
    path('new-traveler', TravelerCreateView.as_view(), name='u_create_traveler'),
    path('list-travelers', TravelerListView.as_view(), name='u_list_travelers'),
    path('traveler-profile/traveler=<traveler_id>',
        TravelerDetailView.as_view(), name='u_traveler_details'),
    path('edit-traveler/traveler=<traveler_id>',
        TravelerUpdateView.as_view(), name='u_edit_traveler'),
    # Approver views urls
    path('new-approver', ApproverCreateView.as_view(), name='create_approver'),
    path('update-approver/approver=<approver_id>', ApproverUpdateView.as_view(),
        name='update_approver'),
    path('approver-details/approver=<approver_id>', ApproverDetailView.as_view(), 
        name='view_approver'),
    path('list-approvers', ApproverListView.as_view(), name='list_approvers'),
    path('delete-approver/approver=<approver_id>', ApproverDeleteView.as_view(),
        name='delete_approver'),
    # CountrySecurityLevel views urls
    path('new-country', CountrySecurityLevelCreateView.as_view(), name='create_country'),
    path('update-country/country=<country_id>', CountrySecurityLevelUpdateView.as_view(),
        name='update_country'),
    path('country-details/country=<country_id>', CountrySecurityLevelDetailView.as_view(),
        name='view_country'),
    path('list-country', CountrySecurityLevelListView.as_view(), name='list_countries'),
    path('delete-country/country=<country_id>', CountrySecurityLevelDeleteView.as_view(),
        name='delete_country'),
]
