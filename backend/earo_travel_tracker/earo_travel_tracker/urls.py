"""earo_travel_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
# Earo_travel_tracker imports
from traveler.urls import api_url_patterns as traveler_api
from traveler.urls import urlpatterns as traveler
from trip.urls import api_url_patterns as trip_api
from trip.urls import urlpatterns as trip


# url patterns for restful APIs
api_urlpatterns = [
    path('traveler/', include(traveler_api)),
    path('trip/', include(trip_api)),
]

# All url patterns
urlpatterns = [
    path('administration/', admin.site.urls),
    path('admin/', include('grappelli.urls')),
    path('api/', include(api_urlpatterns)),
    path('traveler/', include(traveler)),
    path('trip/', include(trip)),
    path('accounts/', include('django.contrib.auth.urls')),
    # Temporary redirect for domain root
    path('', RedirectView.as_view(pattern_name='u_create_trip')),
]
