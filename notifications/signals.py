# Notification signals for Premium HMS
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification, NotificationType

User = get_user_model()

@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """Create a welcome notification for new users"""
    if created:
        try:
            # Get or create a welcome notification type
            welcome_type, _ = NotificationType.objects.get_or_create(
                name="Welcome",
                defaults={
                    'description': 'Welcome notifications for new users',
                    'priority': 'LOW',
                    'is_system_generated': True
                }
            )

            Notification.objects.create(
                recipient=instance,
                notification_type=welcome_type,
                title="Welcome to Premium HMS",
                message=f"Welcome {instance.get_full_name() or instance.email}! Your account has been created successfully.",
                channel="IN_APP"
            )
        except Exception as e:
            # Silently fail if notification creation fails
            pass
