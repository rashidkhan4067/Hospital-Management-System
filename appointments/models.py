from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

class Appointment(models.Model):
    """Appointment booking system"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    APPOINTMENT_TYPES = [
        ('CONSULTATION', 'Consultation'),
        ('FOLLOW_UP', 'Follow-up'),
        ('EMERGENCY', 'Emergency'),
        ('ROUTINE_CHECKUP', 'Routine Checkup'),
    ]
    
    appointment_id = models.CharField(max_length=12, unique=True, editable=False)
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='CONSULTATION')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_id']),
            models.Index(fields=['patient', '-appointment_date']),
            models.Index(fields=['doctor', '-appointment_date']),
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient.full_name} with {self.doctor.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.appointment_id:
            # Generate unique appointment ID
            self.appointment_id = f"A{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def clean(self):
        # Validate appointment time is within doctor's schedule
        from datetime import datetime, time
        
        if self.appointment_date and self.appointment_time:
            # Check if appointment is in the past
            appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
            if appointment_datetime < datetime.now():
                raise ValidationError("Cannot book appointments in the past")
            
            # Check if doctor is available on this day
            day_of_week = self.appointment_date.weekday()
            schedule = self.doctor.schedules.filter(
                day_of_week=day_of_week,
                is_active=True
            ).first()
            
            if not schedule:
                raise ValidationError(
                    f"Doctor is not available on {self.appointment_date.strftime('%A')}"
                )
            
            # Check if appointment time is within schedule
            if not (schedule.start_time <= self.appointment_time <= schedule.end_time):
                raise ValidationError(
                    f"Appointment time must be between {schedule.start_time} and {schedule.end_time}"
                )
    
    @property
    def end_time(self):
        from datetime import datetime, timedelta
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        end_datetime = appointment_datetime + timedelta(minutes=self.duration_minutes)
        return end_datetime.time()
    
    @property
    def is_upcoming(self):
        from datetime import datetime, date
        today = date.today()
        return self.appointment_date >= today and self.status in ['PENDING', 'CONFIRMED']


class AppointmentHistory(models.Model):
    """Track appointment status changes"""
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_status = models.CharField(max_length=10)
    new_status = models.CharField(max_length=10)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.appointment.appointment_id} - {self.old_status} → {self.new_status}"


class Prescription(models.Model):
    """Digital prescriptions linked to appointments"""
    
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='prescription_detail'
    )
    medicines = models.TextField(help_text="List of prescribed medicines with dosage")
    tests = models.TextField(blank=True, help_text="Recommended tests")
    instructions = models.TextField(blank=True, help_text="Special instructions for patient")
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription for {self.appointment.patient.full_name} - {self.created_at.strftime('%Y-%m-%d')}"
