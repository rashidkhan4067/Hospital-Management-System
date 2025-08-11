from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PatientProfile
import uuid

User = get_user_model()

@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    """
    Automatically create PatientProfile when a new user with PATIENT role is created
    """
    if created and instance.role == 'PATIENT':
        try:
            PatientProfile.objects.create(user=instance)
        except Exception as e:
            # Silently fail if profile creation fails
            pass