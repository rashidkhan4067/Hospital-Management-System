"""
Premium HMS API Tests
Comprehensive test suite for REST API endpoints
"""

import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from patients.models import PatientProfile
from doctors.models import DoctorProfile, Department
from appointments.models import Appointment
from billing.models import Bill

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """Base test case with common setup for API tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
        
        self.doctor_user = User.objects.create_user(
            email='doctor@test.com',
            password='testpass123',
            first_name='Dr. John',
            last_name='Smith',
            role='DOCTOR'
        )
        
        self.patient_user = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Doe',
            role='PATIENT'
        )
        
        # Create department
        self.department = Department.objects.create(
            name='Cardiology',
            description='Heart and cardiovascular care'
        )
        
        # Create doctor profile
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            department=self.department,
            specialization='Cardiology',
            license_number='MD123456',
            experience_years=10,
            consultation_fee=Decimal('200.00')
        )
        
        # Create patient profile
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            blood_group='O+',
            emergency_contact_name='John Doe',
            emergency_contact_phone='555-0123'
        )
        
        # Set up API client
        self.client = APIClient()
    
    def get_jwt_token(self, user):
        """Get JWT token for user authentication."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authenticate_user(self, user):
        """Authenticate user for API requests."""
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class AuthenticationAPITests(BaseAPITestCase):
    """Test authentication endpoints."""
    
    def test_token_obtain_pair(self):
        """Test JWT token generation."""
        url = reverse('api:token_obtain_pair')
        data = {
            'email': 'admin@test.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """Test JWT token refresh."""
        # Get initial tokens
        refresh = RefreshToken.for_user(self.admin_user)
        
        url = reverse('api:token_refresh')
        data = {'refresh': str(refresh)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        url = reverse('api:token_obtain_pair')
        data = {
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PatientAPITests(BaseAPITestCase):
    """Test patient-related API endpoints."""
    
    def test_list_patients_as_admin(self):
        """Test listing patients as admin user."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:patient-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user']['email'], 'patient@test.com')
    
    def test_list_patients_as_patient(self):
        """Test that patients can only see their own data."""
        self.authenticate_user(self.patient_user)
        
        url = reverse('api:v1:patient-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user']['email'], 'patient@test.com')
    
    def test_create_patient_as_admin(self):
        """Test creating a new patient as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:patient-list')
        data = {
            'user': {
                'email': 'newpatient@test.com',
                'first_name': 'New',
                'last_name': 'Patient',
                'phone_number': '555-0124'
            },
            'blood_group': 'A+',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '555-0125'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'newpatient@test.com')
        self.assertEqual(response.data['blood_group'], 'A+')
    
    def test_patient_statistics(self):
        """Test patient statistics endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:patient-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_patients', response.data)
        self.assertIn('blood_group_distribution', response.data)
        self.assertIn('age_distribution', response.data)


class DoctorAPITests(BaseAPITestCase):
    """Test doctor-related API endpoints."""
    
    def test_list_doctors(self):
        """Test listing doctors."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:doctor-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user']['email'], 'doctor@test.com')
    
    def test_available_doctors(self):
        """Test available doctors endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:doctor-available')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_doctor_schedule(self):
        """Test doctor schedule endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:doctor-schedule', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('doctor', response.data)
        self.assertIn('schedule', response.data)


class AppointmentAPITests(BaseAPITestCase):
    """Test appointment-related API endpoints."""
    
    def setUp(self):
        super().setUp()
        
        # Create test appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor_profile,
            appointment_type='CONSULTATION',
            appointment_date='2024-01-15',
            appointment_time='10:00:00',
            symptoms='Chest pain'
        )
    
    def test_list_appointments_as_admin(self):
        """Test listing appointments as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_appointments_as_patient(self):
        """Test that patients can only see their appointments."""
        self.authenticate_user(self.patient_user)
        
        url = reverse('api:v1:appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['patient_name'], 'Jane Doe')
    
    def test_list_appointments_as_doctor(self):
        """Test that doctors can only see their appointments."""
        self.authenticate_user(self.doctor_user)
        
        url = reverse('api:v1:appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['doctor_name'], 'Dr. John Smith')
    
    def test_upcoming_appointments(self):
        """Test upcoming appointments endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:appointment-upcoming')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_today_appointments(self):
        """Test today's appointments endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:appointment-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('date', response.data)
        self.assertIn('appointments', response.data)
        self.assertIn('total', response.data)


class BillingAPITests(BaseAPITestCase):
    """Test billing-related API endpoints."""
    
    def setUp(self):
        super().setUp()
        
        # Create test appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor_profile,
            appointment_type='CONSULTATION',
            appointment_date='2024-01-15',
            appointment_time='10:00:00'
        )
        
        # Create test bill
        self.bill = Bill.objects.create(
            patient=self.patient_profile,
            appointment=self.appointment,
            subtotal=Decimal('200.00'),
            tax_amount=Decimal('20.00'),
            total_amount=Decimal('220.00'),
            status='SENT'
        )
    
    def test_list_bills_as_admin(self):
        """Test listing bills as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:bill-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_bills_as_patient(self):
        """Test that patients can only see their bills."""
        self.authenticate_user(self.patient_user)
        
        url = reverse('api:v1:bill-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['patient_name'], 'Jane Doe')
    
    def test_billing_summary(self):
        """Test billing summary endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:v1:bill-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_bills', response.data)
        self.assertIn('total_amount', response.data)
        self.assertIn('outstanding_amount', response.data)


class SystemAPITests(BaseAPITestCase):
    """Test system-related API endpoints."""
    
    def test_health_check(self):
        """Test system health check endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('checks', response.data)
    
    def test_system_status(self):
        """Test system status endpoint."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('api:system_status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('system_info', response.data)
    
    def test_api_root(self):
        """Test API root endpoint."""
        url = reverse('api:api_root')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('version', response.data)
        self.assertIn('endpoints', response.data)


class PermissionTests(BaseAPITestCase):
    """Test API permissions and access control."""
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        url = reverse('api:v1:patient-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_patient_cannot_access_admin_endpoints(self):
        """Test that patients cannot access admin-only endpoints."""
        self.authenticate_user(self.patient_user)
        
        # Try to create a doctor (admin only)
        url = reverse('api:v1:doctor-list')
        data = {
            'user': {
                'email': 'newdoctor@test.com',
                'first_name': 'New',
                'last_name': 'Doctor'
            },
            'department': self.department.id,
            'specialization': 'General Medicine'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should be forbidden or not found depending on permission implementation
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_doctor_can_access_own_data(self):
        """Test that doctors can access their own data."""
        self.authenticate_user(self.doctor_user)
        
        url = reverse('api:v1:doctor-detail', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'doctor@test.com')
