from django.apps import AppConfig


class MedicalRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medical_records'
    verbose_name = 'Premium HMS Medical Records'
    
    def ready(self):
        """Initialize medical records signals when app is ready."""
        import medical_records.signals
