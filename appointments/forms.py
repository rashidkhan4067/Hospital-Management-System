from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from doctors.models import DoctorProfile
from patients.models import PatientProfile

class AppointmentForm(forms.ModelForm):
    """Form for creating/updating appointments (admin use)"""
    
    class Meta:
        model = Appointment
        exclude = ['created_at', 'updated_at']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class BookAppointmentForm(forms.ModelForm):
    """Form for patients to book appointments"""
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.role == 'PATIENT':
            # Filter doctors who are available
            self.fields['doctor'].queryset = DoctorProfile.objects.filter(
                is_available=True
            ).select_related('user', 'department')
        elif user and user.role == 'ADMIN':
            self.fields['doctor'].queryset = DoctorProfile.objects.filter(
                is_available=True
            ).select_related('user', 'department')
    
    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date
    
    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        
        if doctor and appointment_date and appointment_time:
            # Check for conflicting appointments
            existing = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['PENDING', 'CONFIRMED']
            ).exists()
            
            if existing:
                raise forms.ValidationError(
                    "This time slot is already booked. Please choose another time."
                )
        
        return cleaned_data
    
    class Meta:
        model = Appointment
        exclude = ['patient', 'created_at', 'updated_at', 'status']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'value': 30}),
            'symptoms': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
