from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Premium HMS API'
    
    def ready(self):
        """Initialize API configurations when app is ready."""
        pass
