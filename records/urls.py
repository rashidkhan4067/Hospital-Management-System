from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('', views.MedicalRecordsListView.as_view(), name='record_list'),
    path('create/', views.MedicalRecordCreateView.as_view(), name='record_create'),
    path('<int:pk>/', views.MedicalRecordDetailView.as_view(), name='record_detail'),
    path('<int:pk>/edit/', views.MedicalRecordUpdateView.as_view(), name='record_edit'),
    path('<int:pk>/delete/', views.MedicalRecordDeleteView.as_view(), name='record_delete'),
    path('patient/<int:patient_id>/', views.PatientRecordsView.as_view(), name='patient_records'),
    path('search/', views.RecordSearchView.as_view(), name='record_search'),
]
