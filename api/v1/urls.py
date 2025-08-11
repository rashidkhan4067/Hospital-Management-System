"""
Premium HMS API v1 URLs
Comprehensive RESTful API endpoints for all system modules
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PatientViewSet,
    DoctorViewSet,
    AppointmentViewSet,
    BillViewSet,
    DepartmentViewSet,
    MedicalRecordViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'billing', BillViewSet, basename='bill')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')

app_name = 'v1'

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # Custom endpoints can be added here
    # path('custom-endpoint/', CustomView.as_view(), name='custom_endpoint'),
]
