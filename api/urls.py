"""
Premium Hospital Management System API URLs
Ultra-modern RESTful API with versioning and comprehensive endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .v1 import urls as v1_urls
from .views import (
    APIRootView,
    HealthCheckView,
    SystemStatusView,
)

app_name = 'api'

# API Documentation URLs
doc_patterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]

# Authentication URLs
auth_patterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# System URLs
system_patterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('status/', SystemStatusView.as_view(), name='system_status'),
]

urlpatterns = [
    # API Root
    path('', APIRootView.as_view(), name='api_root'),
    
    # Documentation
    path('', include(doc_patterns)),
    
    # Authentication
    path('auth/', include(auth_patterns)),
    
    # System Monitoring
    path('system/', include(system_patterns)),
    
    # API Versions
    path('v1/', include(v1_urls)),
]
