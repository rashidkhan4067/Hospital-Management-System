from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

class PatientTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email='admin@hospital.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
        self.patient_user = User.objects.create_user(
            email='patient@hospital.com',
            password='patient123',
            first_name='Patient',
            last_name='User',
            role='PATIENT'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            gender='M',
            address='123 Main St',
            phone='+1234567890',
            emergency_contact='John Doe',
            emergency_phone='+1987654321'
        )

    def test_patient_creation(self):
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(self.patient.user.email, 'patient@hospital.com')
        self.assertEqual(self.patient.gender, 'M')

    def test_patient_list_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('patient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient User')

    def test_patient_detail_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('patient_detail', args=[self.patient.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123 Main St')

    def test_patient_create_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.post(reverse('patient_create'), {
            'email': 'newpatient@hospital.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'Patient',
            'date_of_birth': '1985-05-15',
            'gender': 'F',
            'address': '456 Oak Ave',
            'phone': '+1122334455',
            'emergency_contact': 'Jane Smith',
            'emergency_phone': '+1555666777'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), 2)
        self.assertContains(response, 'New Patient')

    def test_patient_update_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.post(reverse('patient_update', args=[self.patient.id]), {
            'first_name': 'Updated',
            'last_name': 'Patient',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'address': '789 Pine Rd',
            'phone': '+1234567890',
            'emergency_contact': 'John Doe',
            'emergency_phone': '+1987654321'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.user.first_name, 'Updated')
        self.assertEqual(self.patient.address, '789 Pine Rd')
