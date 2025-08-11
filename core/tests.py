from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CoreViewsTests(TestCase):
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
        self.patient_user = User.objects.create_user(
            email='patient@hospital.com',
            password='patient123',
            first_name='Patient',
            last_name='User',
            role='PATIENT'
        )

    def test_dashboard_view_for_admin(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_dashboard_view_for_doctor(self):
        self.client.login(email='doctor@hospital.com', password='doctor123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Today\'s Appointments')

    def test_dashboard_view_for_patient(self):
        self.client.login(email='patient@hospital.com', password='patient123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upcoming Appointments')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')

    def test_login_functionality(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin@hospital.com',
            'password': 'admin123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_logout_functionality(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')
