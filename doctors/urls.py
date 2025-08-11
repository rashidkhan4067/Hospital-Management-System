from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.DoctorListView.as_view(), name='doctor_list'),
    path('create/', views.DoctorCreateView.as_view(), name='doctor_create'),
    path('<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor_edit'),
    path('<int:pk>/schedule/', views.DoctorScheduleView.as_view(), name='doctor_schedule'),
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('search/', views.DoctorSearchView.as_view(), name='doctor_search'),
]
