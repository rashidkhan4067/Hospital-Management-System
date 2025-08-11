from django.db import models
from django.conf import settings
import uuid

class Department(models.Model):
    """Hospital departments"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        'DoctorProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def doctor_count(self):
        return self.doctor_profiles.count()


class DoctorProfile(models.Model):
    """Extended doctor information linked to User model"""
    
    SPECIALIZATIONS = [
        ('CARDIOLOGY', 'Cardiology'),
        ('NEUROLOGY', 'Neurology'),
        ('PEDIATRICS', 'Pediatrics'),
        ('ORTHOPEDICS', 'Orthopedics'),
        ('DERMATOLOGY', 'Dermatology'),
        ('OPHTHALMOLOGY', 'Ophthalmology'),
        ('GYNECOLOGY', 'Gynecology'),
        ('PSYCHIATRY', 'Psychiatry'),
        ('GENERAL', 'General Medicine'),
        ('SURGERY', 'General Surgery'),
        ('ENT', 'Ear, Nose & Throat'),
        ('DENTISTRY', 'Dentistry'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    doctor_id = models.CharField(max_length=10, unique=True, editable=False)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATIONS)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='doctor_profiles'
    )
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=200)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True, help_text="Brief description about the doctor")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['doctor_id']),
            models.Index(fields=['specialization']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
    
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            # Generate unique doctor ID
            self.doctor_id = f"D{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name()}"
    
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


class Schedule(models.Model):
    """Doctor's weekly schedule"""
    
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_appointments = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['doctor', 'day_of_week']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.full_name} - {self.get_day_of_week_display()}"
    
    @property
    def day_name(self):
        return self.get_day_of_week_display()
