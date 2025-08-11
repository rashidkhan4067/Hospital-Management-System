from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.AppointmentListView.as_view(), name='appointment_list'),
    path('create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_edit'),
    path('<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointment_cancel'),
    path('<int:pk>/confirm/', views.AppointmentConfirmView.as_view(), name='appointment_confirm'),
    path('calendar/', views.AppointmentCalendarView.as_view(), name='appointment_calendar'),
    path('book/', views.BookAppointmentView.as_view(), name='book_appointment'),
    path('my-appointments/', views.MyAppointmentsView.as_view(), name='my_appointments'),
]
