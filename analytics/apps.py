from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Premium HMS Analytics'
    
    def ready(self):
        """Initialize analytics when app is ready."""
        pass
