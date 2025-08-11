"""
Premium HMS WebSocket Consumers
Real-time communication handlers for notifications and live updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    Handles user-specific notification delivery and real-time updates.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'
        
        # Join user-specific group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification stream',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_notification_read':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_read(notification_id)
            elif message_type == 'get_unread_count':
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': count
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def notification_message(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification'],
            'timestamp': event['timestamp']
        }))
    
    async def system_alert(self, event):
        """Send system alert to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'system_alert',
            'alert': event['alert'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read in database."""
        from .models import Notification
        try:
            notification = Notification.objects.get(
                notification_id=notification_id,
                recipient_id=self.user_id
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for user."""
        from .models import Notification
        return Notification.objects.filter(
            recipient_id=self.user_id,
            status__in=['PENDING', 'SENT', 'DELIVERED']
        ).count()


class AppointmentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time appointment updates.
    
    Handles appointment scheduling, updates, and cancellations.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'appointments_{self.room_name}'
        
        # Join appointment room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave appointment room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'appointment_update':
                # Handle appointment update
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'appointment_message',
                        'message': text_data_json.get('message'),
                        'appointment_id': text_data_json.get('appointment_id'),
                        'timestamp': timezone.now().isoformat()
                    }
                )
        except json.JSONDecodeError:
            pass
    
    async def appointment_message(self, event):
        """Send appointment update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'appointment_update',
            'message': event['message'],
            'appointment_id': event['appointment_id'],
            'timestamp': event['timestamp']
        }))


class SystemStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for system status monitoring.
    
    Provides real-time system health and performance metrics.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_group_name = 'system_status'
        
        # Join system status group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave system status group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def system_status_update(self, event):
        """Send system status update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'system_status',
            'status': event['status'],
            'metrics': event['metrics'],
            'timestamp': event['timestamp']
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality.
    
    Enables communication between patients, doctors, and staff.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join chat room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave chat room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            user_id = text_data_json.get('user_id')
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': user_id,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except (json.JSONDecodeError, KeyError):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
    
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))
