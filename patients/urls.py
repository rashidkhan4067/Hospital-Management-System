from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_edit'),
    path('<int:pk>/medical-records/', views.MedicalRecordListView.as_view(), name='patient_records'),
    path('<int:pk>/medical-records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('search/', views.PatientSearchView.as_view(), name='patient_search'),
]
