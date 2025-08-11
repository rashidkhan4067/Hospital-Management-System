"""
Premium HMS Model Tests
Comprehensive test suite for Django models
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, time, timedelta

from patients.models import PatientProfile
from doctors.models import DoctorProfile, Department, Schedule
from appointments.models import Appointment
from billing.models import Bill, BillItem, Payment
from medical_records.models import (
    MedicalRecord, Prescription, Medication, VitalSigns,
    LabTest, LabOrder, LabResult, ImagingStudy
)
from notifications.models import Notification, NotificationType

User = get_user_model()


class UserModelTests(TestCase):
    """Test custom User model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, 'PATIENT')  # Default role
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(user.email, 'admin@example.com')
        self.assertEqual(user.role, 'ADMIN')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(str(user), 'Test User')
    
    def test_user_full_name(self):
        """Test user full name property."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.get_full_name(), 'Test User')
    
    def test_user_age_calculation(self):
        """Test user age calculation."""
        birth_date = date.today() - timedelta(days=365 * 25)  # 25 years ago
        user = User.objects.create_user(
            email='test@example.com',
            birth_date=birth_date
        )
        
        self.assertEqual(user.age, 25)


class PatientModelTests(TestCase):
    """Test PatientProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='patient@example.com',
            first_name='John',
            last_name='Doe',
            role='PATIENT'
        )
    
    def test_create_patient_profile(self):
        """Test creating a patient profile."""
        patient = PatientProfile.objects.create(
            user=self.user,
            blood_group='O+',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='555-0123'
        )
        
        self.assertEqual(patient.user, self.user)
        self.assertEqual(patient.blood_group, 'O+')
        self.assertTrue(patient.patient_id.startswith('P'))
        self.assertEqual(len(patient.patient_id), 9)  # P + 8 characters
    
    def test_patient_string_representation(self):
        """Test patient string representation."""
        patient = PatientProfile.objects.create(
            user=self.user,
            blood_group='A+'
        )
        
        self.assertEqual(str(patient), f'{patient.patient_id} - John Doe')
    
    def test_patient_full_name_property(self):
        """Test patient full name property."""
        patient = PatientProfile.objects.create(
            user=self.user,
            blood_group='B+'
        )
        
        self.assertEqual(patient.full_name, 'John Doe')


class DoctorModelTests(TestCase):
    """Test DoctorProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='doctor@example.com',
            first_name='Dr. Jane',
            last_name='Smith',
            role='DOCTOR'
        )
        
        self.department = Department.objects.create(
            name='Cardiology',
            description='Heart and cardiovascular care'
        )
    
    def test_create_doctor_profile(self):
        """Test creating a doctor profile."""
        doctor = DoctorProfile.objects.create(
            user=self.user,
            department=self.department,
            specialization='Cardiology',
            license_number='MD123456',
            experience_years=10,
            consultation_fee=Decimal('200.00')
        )
        
        self.assertEqual(doctor.user, self.user)
        self.assertEqual(doctor.department, self.department)
        self.assertEqual(doctor.specialization, 'Cardiology')
        self.assertTrue(doctor.doctor_id.startswith('D'))
        self.assertEqual(doctor.consultation_fee, Decimal('200.00'))
    
    def test_doctor_string_representation(self):
        """Test doctor string representation."""
        doctor = DoctorProfile.objects.create(
            user=self.user,
            department=self.department,
            specialization='Cardiology'
        )
        
        self.assertEqual(str(doctor), f'{doctor.doctor_id} - Dr. Jane Smith (Cardiology)')


class AppointmentModelTests(TestCase):
    """Test Appointment model."""
    
    def setUp(self):
        # Create patient
        self.patient_user = User.objects.create_user(
            email='patient@example.com',
            first_name='John',
            last_name='Doe',
            role='PATIENT'
        )
        self.patient = PatientProfile.objects.create(
            user=self.patient_user,
            blood_group='O+'
        )
        
        # Create doctor
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com',
            first_name='Dr. Jane',
            last_name='Smith',
            role='DOCTOR'
        )
        self.department = Department.objects.create(
            name='Cardiology'
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            department=self.department,
            specialization='Cardiology'
        )
    
    def test_create_appointment(self):
        """Test creating an appointment."""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_type='CONSULTATION',
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            symptoms='Chest pain'
        )
        
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.appointment_type, 'CONSULTATION')
        self.assertTrue(appointment.appointment_id.startswith('A'))
        self.assertEqual(appointment.status, 'PENDING')  # Default status
    
    def test_appointment_end_time_property(self):
        """Test appointment end time calculation."""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            duration_minutes=30
        )
        
        expected_end_time = time(10, 30)
        self.assertEqual(appointment.end_time, expected_end_time)
    
    def test_appointment_is_upcoming_property(self):
        """Test appointment is_upcoming property."""
        # Future appointment
        future_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0)
        )
        
        # Past appointment
        past_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today() - timedelta(days=1),
            appointment_time=time(10, 0)
        )
        
        self.assertTrue(future_appointment.is_upcoming)
        self.assertFalse(past_appointment.is_upcoming)


class BillModelTests(TestCase):
    """Test billing models."""
    
    def setUp(self):
        # Create patient
        self.patient_user = User.objects.create_user(
            email='patient@example.com',
            first_name='John',
            last_name='Doe',
            role='PATIENT'
        )
        self.patient = PatientProfile.objects.create(
            user=self.patient_user,
            blood_group='O+'
        )
        
        # Create doctor
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com',
            first_name='Dr. Jane',
            last_name='Smith',
            role='DOCTOR'
        )
        self.department = Department.objects.create(name='Cardiology')
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            department=self.department
        )
        
        # Create appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today(),
            appointment_time=time(10, 0)
        )
    
    def test_create_bill(self):
        """Test creating a bill."""
        bill = Bill.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            subtotal=Decimal('200.00'),
            tax_amount=Decimal('20.00'),
            total_amount=Decimal('220.00')
        )
        
        self.assertEqual(bill.patient, self.patient)
        self.assertEqual(bill.appointment, self.appointment)
        self.assertEqual(bill.subtotal, Decimal('200.00'))
        self.assertEqual(bill.total_amount, Decimal('220.00'))
        self.assertTrue(bill.bill_number.startswith('B'))
        self.assertEqual(bill.status, 'DRAFT')  # Default status
    
    def test_bill_balance_due_property(self):
        """Test bill balance due calculation."""
        bill = Bill.objects.create(
            patient=self.patient,
            total_amount=Decimal('220.00'),
            paid_amount=Decimal('100.00')
        )
        
        self.assertEqual(bill.balance_due, Decimal('120.00'))
    
    def test_bill_is_fully_paid_property(self):
        """Test bill is_fully_paid property."""
        # Fully paid bill
        paid_bill = Bill.objects.create(
            patient=self.patient,
            total_amount=Decimal('220.00'),
            paid_amount=Decimal('220.00')
        )
        
        # Partially paid bill
        unpaid_bill = Bill.objects.create(
            patient=self.patient,
            total_amount=Decimal('220.00'),
            paid_amount=Decimal('100.00')
        )
        
        self.assertTrue(paid_bill.is_fully_paid)
        self.assertFalse(unpaid_bill.is_fully_paid)


class MedicalRecordModelTests(TestCase):
    """Test medical record models."""
    
    def setUp(self):
        # Create patient
        self.patient_user = User.objects.create_user(
            email='patient@example.com',
            first_name='John',
            last_name='Doe',
            role='PATIENT'
        )
        self.patient = PatientProfile.objects.create(
            user=self.patient_user,
            blood_group='O+'
        )
        
        # Create doctor
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com',
            first_name='Dr. Jane',
            last_name='Smith',
            role='DOCTOR'
        )
        self.department = Department.objects.create(name='Cardiology')
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            department=self.department
        )
    
    def test_create_medical_record(self):
        """Test creating a medical record."""
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            record_type='CONSULTATION',
            chief_complaint='Chest pain',
            assessment='Possible angina',
            plan='ECG and stress test'
        )
        
        self.assertEqual(record.patient, self.patient)
        self.assertEqual(record.doctor, self.doctor)
        self.assertEqual(record.record_type, 'CONSULTATION')
        self.assertTrue(record.record_id.startswith('MR'))
        self.assertEqual(record.priority, 'MEDIUM')  # Default priority
    
    def test_create_vital_signs(self):
        """Test creating vital signs."""
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            chief_complaint='Routine checkup'
        )
        
        vitals = VitalSigns.objects.create(
            medical_record=record,
            patient=self.patient,
            temperature=Decimal('98.6'),
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=72,
            weight=Decimal('150.0'),
            height=70
        )
        
        self.assertEqual(vitals.temperature, Decimal('98.6'))
        self.assertEqual(vitals.blood_pressure, '120/80')
        self.assertEqual(vitals.bmi, 21.5)  # Calculated BMI
    
    def test_create_prescription(self):
        """Test creating a prescription."""
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            chief_complaint='Hypertension'
        )
        
        prescription = Prescription.objects.create(
            medical_record=record,
            patient=self.patient,
            doctor=self.doctor,
            start_date=date.today(),
            general_instructions='Take with food'
        )
        
        self.assertEqual(prescription.patient, self.patient)
        self.assertEqual(prescription.doctor, self.doctor)
        self.assertTrue(prescription.prescription_id.startswith('RX'))
        self.assertEqual(prescription.status, 'ACTIVE')  # Default status
        self.assertFalse(prescription.is_expired)


class NotificationModelTests(TestCase):
    """Test notification models."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.notification_type = NotificationType.objects.create(
            name='Test Notification',
            description='Test notification type'
        )
    
    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            notification_type=self.notification_type,
            recipient=self.user,
            title='Test Notification',
            message='This is a test notification',
            channel='IN_APP'
        )
        
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertTrue(notification.notification_id.startswith('N'))
        self.assertEqual(notification.status, 'PENDING')  # Default status
    
    def test_notification_status_methods(self):
        """Test notification status update methods."""
        notification = Notification.objects.create(
            notification_type=self.notification_type,
            recipient=self.user,
            title='Test',
            message='Test',
            channel='EMAIL'
        )
        
        # Test mark as sent
        notification.mark_as_sent()
        self.assertEqual(notification.status, 'SENT')
        self.assertIsNotNone(notification.sent_at)
        
        # Test mark as delivered
        notification.mark_as_delivered()
        self.assertEqual(notification.status, 'DELIVERED')
        self.assertIsNotNone(notification.delivered_at)
        
        # Test mark as read
        notification.mark_as_read()
        self.assertEqual(notification.status, 'READ')
        self.assertIsNotNone(notification.read_at)
