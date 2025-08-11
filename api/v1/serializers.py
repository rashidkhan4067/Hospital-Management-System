"""
Premium HMS API v1 Serializers
Advanced serializers with comprehensive validation and nested relationships
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from patients.models import PatientProfile, MedicalRecord
from doctors.models import DoctorProfile, Department, Schedule
from appointments.models import Appointment
from billing.models import Bill, BillItem, Payment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with security considerations."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'birth_date', 'address', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True}
        }


class PatientProfileSerializer(serializers.ModelSerializer):
    """Comprehensive Patient Profile serializer with nested user data."""
    
    user = UserSerializer()
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'patient_id', 'blood_group', 'emergency_contact_name',
            'emergency_contact_phone', 'medical_history', 'current_medications',
            'full_name', 'age', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create patient with nested user data."""
        user_data = validated_data.pop('user')
        user_data['role'] = 'PATIENT'
        user = User.objects.create_user(**user_data)
        patient = PatientProfile.objects.create(user=user, **validated_data)
        return patient
    
    def update(self, instance, validated_data):
        """Update patient with nested user data."""
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer with doctor count."""
    
    doctor_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'head', 'doctor_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class ScheduleSerializer(serializers.ModelSerializer):
    """Doctor schedule serializer."""
    
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'day_of_week', 'day_name', 'start_time', 'end_time',
            'max_appointments', 'is_active'
        ]
        read_only_fields = ['id']


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Comprehensive Doctor Profile serializer with nested relationships."""
    
    user = UserSerializer()
    department_name = serializers.CharField(source='department.name', read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'doctor_id', 'department', 'department_name',
            'specialization', 'license_number', 'experience_years',
            'qualification', 'consultation_fee', 'bio', 'is_available',
            'schedules', 'full_name', 'age', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'doctor_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create doctor with nested user data."""
        user_data = validated_data.pop('user')
        user_data['role'] = 'DOCTOR'
        user = User.objects.create_user(**user_data)
        doctor = DoctorProfile.objects.create(user=user, **validated_data)
        return doctor
    
    def update(self, instance, validated_data):
        """Update doctor with nested user data."""
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AppointmentSerializer(serializers.ModelSerializer):
    """Comprehensive Appointment serializer with nested relationships."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    department_name = serializers.CharField(source='doctor.department.name', read_only=True)
    end_time = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_id', 'patient', 'patient_name', 'doctor',
            'doctor_name', 'department_name', 'appointment_type',
            'appointment_date', 'appointment_time', 'end_time',
            'duration_minutes', 'status', 'symptoms', 'notes',
            'prescription', 'is_upcoming', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'appointment_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Custom validation for appointment scheduling."""
        # Add custom validation logic here
        return data


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Medical Record serializer with comprehensive patient and doctor info."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'diagnosis', 'treatment', 'notes', 'prescription',
            'visit_date', 'next_appointment'
        ]
        read_only_fields = ['id', 'visit_date']


class BillItemSerializer(serializers.ModelSerializer):
    """Bill Item serializer."""
    
    class Meta:
        model = BillItem
        fields = ['id', 'service', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['id', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer."""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'amount', 'payment_method',
            'payment_date', 'transaction_id', 'notes', 'received_by',
            'created_at'
        ]
        read_only_fields = ['id', 'payment_id', 'created_at']


class BillSerializer(serializers.ModelSerializer):
    """Comprehensive Bill serializer with nested items and payments."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    items = BillItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    balance_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'patient', 'patient_name', 'appointment',
            'issue_date', 'due_date', 'subtotal', 'tax_amount',
            'discount_amount', 'total_amount', 'paid_amount', 'balance_due',
            'status', 'payment_method', 'notes', 'items', 'payments',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'bill_number', 'created_at', 'updated_at']
    
    def get_balance_due(self, obj):
        """Calculate balance due."""
        return obj.total_amount - obj.paid_amount
