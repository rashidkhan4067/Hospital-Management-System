from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment

User = get_user_model()

class AppointmentTests(TestCase):
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
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='Cardiology',
            license_number='DOC12345'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            gender='M'
        )
        
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date='2025-08-01',
            appointment_time='10:00:00',
            reason='Heart checkup',
            status='PENDING'
        )

    def test_appointment_creation(self):
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(self.appointment.reason, 'Heart checkup')
        self.assertEqual(self.appointment.status, 'PENDING')

    def test_appointment_list_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('appointment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Heart checkup')

    def test_appointment_create_view(self):
        self.client.login(email='patient@hospital.com', password='patient123')
        response = self.client.post(reverse('appointment_create'), {
            'doctor': self.doctor.id,
            'appointment_date': '2025-08-02',
            'appointment_time': '14:00:00',
            'reason': 'Follow-up visit',
            'status': 'PENDING'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 2)
        self.assertContains(response, 'Follow-up visit')

    def test_appointment_update_view(self):
        self.client.login(email='doctor@hospital.com', password='doctor123')
        response = self.client.post(reverse('appointment_update', args=[self.appointment.id]), {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'appointment_date': '2025-08-01',
            'appointment_time': '11:00:00',
            'reason': 'Heart checkup - urgent',
            'status': 'CONFIRMED'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'CONFIRMED')
        self.assertEqual(self.appointment.appointment_time.strftime('%H:%M:%S'), '11:00:00')
