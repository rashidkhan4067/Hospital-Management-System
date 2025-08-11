from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    # Add core app URL patterns here
]