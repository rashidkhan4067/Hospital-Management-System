from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('create/', views.NotificationCreateView.as_view(), name='notification_create'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('<int:pk>/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
    path('settings/', views.NotificationSettingsView.as_view(), name='settings'),
    path('api/unread-count/', views.UnreadCountAPIView.as_view(), name='unread_count_api'),
]
