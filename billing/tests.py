from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from billing.models import Bill

User = get_user_model()

class BillingTests(TestCase):
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
            license_number='DOC12345',
            consultation_fee=200.00
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
            status='COMPLETED'
        )
        
        self.bill = Bill.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment=self.appointment,
            bill_number='BILL-001',
            consultation_fee=200.00,
            medication_fee=50.00,
            other_fee=30.00,
            status='PENDING'
        )

    def test_bill_creation(self):
        self.assertEqual(Bill.objects.count(), 1)
        self.assertEqual(self.bill.bill_number, 'BILL-001')
        self.assertEqual(self.bill.total_amount, 280.00)
        self.assertEqual(self.bill.status, 'PENDING')

    def test_bill_list_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('bill_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BILL-001')

    def test_bill_detail_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.get(reverse('bill_detail', args=[self.bill.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '280.00')

    def test_bill_create_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.post(reverse('bill_create'), {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'appointment': self.appointment.id,
            'bill_number': 'BILL-002',
            'consultation_fee': 200.00,
            'medication_fee': 75.00,
            'other_fee': 25.00,
            'status': 'PENDING'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Bill.objects.count(), 2)
        self.assertContains(response, 'BILL-002')

    def test_bill_update_view(self):
        self.client.login(email='admin@hospital.com', password='admin123')
        response = self.client.post(reverse('bill_update', args=[self.bill.id]), {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'appointment': self.appointment.id,
            'bill_number': 'BILL-001',
            'consultation_fee': 200.00,
            'medication_fee': 60.00,
            'other_fee': 40.00,
            'status': 'PAID'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.bill.refresh_from_db()
        self.assertEqual(self.bill.total_amount, 300.00)
        self.assertEqual(self.bill.status, 'PAID')
