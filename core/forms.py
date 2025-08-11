from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with role selection"""
    
    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
    ]
    
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial='PATIENT')
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # Create profile based on role
            if user.role == 'PATIENT':
                from patients.models import PatientProfile
                PatientProfile.objects.create(user=user)
            elif user.role == 'DOCTOR':
                from doctors.models import DoctorProfile
                # For doctors, we need department and other required fields
                # For now, create with minimal data - this should be completed later
                try:
                    from doctors.models import Department
                    default_dept = Department.objects.first()
                    if not default_dept:
                        default_dept = Department.objects.create(
                            name="General Medicine",
                            description="Default department for new doctors"
                        )
                    DoctorProfile.objects.create(
                        user=user,
                        specialization='GENERAL',
                        department=default_dept,
                        license_number=f'LIC{user.id:06d}',
                        qualification='To be updated'
                    )
                except Exception as e:
                    # If doctor profile creation fails, just save the user
                    pass

        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'birth_date', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
