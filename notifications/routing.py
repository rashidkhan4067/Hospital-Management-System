"""
Premium HMS WebSocket Routing
Real-time communication routing for notifications and live updates
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/appointments/(?P<room_name>\w+)/$', consumers.AppointmentConsumer.as_asgi()),
    re_path(r'ws/system/status/$', consumers.SystemStatusConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
