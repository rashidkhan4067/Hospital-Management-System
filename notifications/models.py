"""
Premium HMS Notifications Models
Advanced notification system with multiple delivery channels
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class NotificationType(models.Model):
    """Types of notifications in the system."""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_active = models.BooleanField(default=True)
    
    # Delivery channels
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """Individual notification instances."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
    ]
    
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App'),
        ('WEBSOCKET', 'WebSocket'),
    ]
    
    notification_id = models.CharField(max_length=12, unique=True, editable=False)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # Additional data for the notification
    
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Retry mechanism
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['channel']),
        ]
    
    def __str__(self):
        return f"{self.notification_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.notification_id:
            self.notification_id = f"N{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_as_delivered(self):
        """Mark notification as delivered."""
        self.status = 'DELIVERED'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.status = 'READ'
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at'])
    
    def mark_as_failed(self, error_message=''):
        """Mark notification as failed."""
        self.status = 'FAILED'
        self.error_message = error_message
        self.retry_count += 1
        
        if self.retry_count < self.max_retries:
            # Schedule retry
            self.next_retry_at = timezone.now() + timezone.timedelta(minutes=5 * self.retry_count)
            self.status = 'PENDING'
        
        self.save(update_fields=['status', 'error_message', 'retry_count', 'next_retry_at'])


class NotificationTemplate(models.Model):
    """Templates for different types of notifications."""
    
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='templates')
    channel = models.CharField(max_length=10, choices=Notification.CHANNEL_CHOICES)
    
    subject_template = models.CharField(max_length=200, blank=True)  # For email/SMS
    message_template = models.TextField()
    
    # Template variables documentation
    variables = models.JSONField(default=dict, blank=True, help_text="Available template variables")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['notification_type', 'channel']
        ordering = ['notification_type', 'channel']
    
    def __str__(self):
        return f"{self.notification_type.name} - {self.channel}"


class NotificationPreference(models.Model):
    """User preferences for notifications."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Global preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_start_time = models.TimeField(default='22:00')
    quiet_end_time = models.TimeField(default='08:00')
    
    # Frequency settings
    digest_enabled = models.BooleanField(default=False)
    digest_frequency = models.CharField(
        max_length=10,
        choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly')],
        default='DAILY'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user.get_full_name()}"


class NotificationTypePreference(models.Model):
    """User preferences for specific notification types."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'notification_type']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.notification_type.name}"


class NotificationLog(models.Model):
    """Log of all notification activities for auditing."""
    
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
        ('RETRIED', 'Retried'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.notification.notification_id} - {self.action}"
