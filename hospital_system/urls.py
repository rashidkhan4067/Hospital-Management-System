"""
Premium Hospital Management System URL Configuration
Ultra-modern healthcare management platform with advanced API integration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Admin customization
admin.site.site_header = "Premium HMS Administration"
admin.site.site_title = "Premium HMS Admin"
admin.site.index_title = "Welcome to Premium HMS Administration"

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Core application
    path('', include('core.urls')),

    # Main application modules
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('billing/', include('billing.urls')),

    # Additional modules
    path('analytics/', include('hospital_analytics.urls')),
    path('medical-records/', include('records.urls')),
    # path('notifications/', include('alerts.urls')),  # Temporarily disabled

    # API endpoints (commented out until DRF is installed)
    # path('api/', include('api.urls')),

    # Health check endpoint
    # path('health/', RedirectView.as_view(url='/api/system/health/', permanent=False)),
]

# Development settings
if settings.DEBUG:
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar (commented out)
    # if 'debug_toolbar' in settings.INSTALLED_APPS:
    #     import debug_toolbar
    #     urlpatterns = [
    #         path('__debug__/', include(debug_toolbar.urls)),
    #     ] + urlpatterns

# Serve static files during development
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()