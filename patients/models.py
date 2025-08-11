from django.db import models
from django.conf import settings
from core.models import User
import uuid

class PatientProfile(models.Model):
    """Extended patient information linked to User model"""
    
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    patient_id = models.CharField(max_length=10, unique=True, editable=False)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    medical_history = models.TextField(blank=True, help_text="Previous illnesses, surgeries, allergies")
    current_medications = models.TextField(blank=True, help_text="Current medications being taken")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.patient_id}"
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Generate unique patient ID
            self.patient_id = f"P{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def phone(self):
        return self.user.phone_number
    
    @property
    def age(self):
        from datetime import date
        if self.user.birth_date:
            today = date.today()
            return today.year - self.user.birth_date.year - (
                (today.month, today.day) < (self.user.birth_date.month, self.user.birth_date.day)
            )
        return None


class MedicalRecord(models.Model):
    """Medical records for patients"""
    
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='patient_records'
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='doctor_records'
    )
    diagnosis = models.TextField()
    treatment = models.TextField()
    notes = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    visit_date = models.DateTimeField(auto_now_add=True)
    next_appointment = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['patient', '-visit_date']),
            models.Index(fields=['doctor', '-visit_date']),
        ]
    
    def __str__(self):
        return f"Record for {self.patient.full_name} - {self.visit_date.strftime('%Y-%m-%d')}"
