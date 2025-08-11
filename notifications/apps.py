from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Premium HMS Notifications'
    
    def ready(self):
        """Initialize notification signals when app is ready."""
        try:
            import notifications.signals
        except ImportError:
            pass
