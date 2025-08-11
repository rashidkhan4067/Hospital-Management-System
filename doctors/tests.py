from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from doctors.models import Doctor

User = get_user_model()

class DoctorTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email='admin@hospital.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
        self.doctor_user = User.objects.create_user(
            email='doctor@hospital.com',
            password='doctor123',
            first_name='Doctor',
            last_name='User',
            role='DOCTOR'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='Cardiology',
            license_number='DOC12345',
            phone='+1234567890',
            address='123 Medical Center Dr',
            bio='Experienced cardiologist',
            consultation_fee=200.00
        )

    def test_doctor_creation(self):
        self.assertEqual(Doctor.objects.count(), 1)
        self.assertEqual(self.doctor.user.email, 'doctor@hospital.com')
        self.assertEqual(self.doctor.specialization, 'Cardiology')

    def test_doctor_list_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('doctor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Doctor User')

    def test_doctor_detail_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('doctor_detail', args=[self.doctor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cardiology')

    def test_doctor_create_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.post(reverse('doctor_create'), {
            'email': 'newdoctor@hospital.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'Doctor',
            'specialization': 'Neurology',
            'license_number': 'DOC54321',
            'phone': '+1122334455',
            'address': '456 Health Ave',
            'bio': 'Neurology specialist',
            'consultation_fee': 250.00
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Doctor.objects.count(), 2)
        self.assertContains(response, 'New Doctor')

    def test_doctor_update_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.post(reverse('doctor_update', args=[self.doctor.id]), {
            'first_name': 'Updated',
            'last_name': 'Doctor',
            'specialization': 'Cardiology',
            'license_number': 'DOC12345',
            'phone': '+1234567890',
            'address': '789 Medical Park',
            'bio': 'Senior cardiologist',
            'consultation_fee': 250.00
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.user.first_name, 'Updated')
        self.assertEqual(self.doctor.consultation_fee, 250.00)
