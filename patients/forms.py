from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import PatientProfile, MedicalRecord
from core.models import User

class PatientProfileForm(forms.ModelForm):
    """Form for creating/updating patient profile"""

    class Meta:
        model = PatientProfile
        exclude = ['user', 'patient_id', 'created_at', 'updated_at']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'medical_history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Previous medical conditions, surgeries, allergies...'}),
            'current_medications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Current medications and dosages...'}),
        }

class PatientEditForm(forms.ModelForm):
    """Form for editing patient user information"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'birth_date', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class PatientUserForm(UserCreationForm):
    """Form for creating a new patient user"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'birth_date', 'address', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'PATIENT'
        if commit:
            user.save()
        return user


class MedicalRecordForm(forms.ModelForm):
    """Form for creating medical records"""

    class Meta:
        model = MedicalRecord
        exclude = ['patient', 'doctor', 'visit_date', 'created_at', 'updated_at']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'treatment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'prescription': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'next_appointment': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
