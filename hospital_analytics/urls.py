from django.urls import path
from . import views

app_name = 'hospital_analytics'

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('patients/', views.PatientAnalyticsView.as_view(), name='patient_analytics'),
    path('appointments/', views.AppointmentAnalyticsView.as_view(), name='appointment_analytics'),
    path('financial/', views.FinancialAnalyticsView.as_view(), name='financial_analytics'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('export/', views.ExportDataView.as_view(), name='export_data'),
]
