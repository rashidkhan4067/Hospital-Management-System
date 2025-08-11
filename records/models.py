from django.db import models
from django.contrib.auth import get_user_model
from patients.models import PatientProfile
from doctors.models import DoctorProfile

User = get_user_model()

class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='patient_medical_records')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='doctor_medical_records')

    # Medical Information
    diagnosis = models.TextField(help_text="Primary diagnosis")
    treatment = models.TextField(help_text="Treatment provided")
    medications = models.TextField(blank=True, help_text="Prescribed medications")
    notes = models.TextField(blank=True, help_text="Additional notes")

    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Medical Record"
        verbose_name_plural = "Medical Records"

    def __str__(self):
        return f"Medical Record - {self.patient.user.get_full_name()} ({self.created_at.date()})"
