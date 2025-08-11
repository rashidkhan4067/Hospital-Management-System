import random
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from django.contrib.auth import get_user_model
from doctors.models import DoctorProfile, Department
from patients.models import PatientProfile
from appointments.models import Appointment
from billing.models import Bill

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('Deleting existing data...')
        User.objects.all().delete()
        Department.objects.all().delete()
        self.stdout.write('Existing data deleted.')

        self.stdout.write('Populating database...')
        fake = Faker()

        # Create Departments
        departments = []
        for _ in range(5):
            department = Department.objects.create(name=fake.bs())
            departments.append(department)
        self.stdout.write(f'{len(departments)} departments created.')

        # Create Users, Doctors, and Patients
        users = []
        for i in range(20): # Create more users to ensure we have enough of each role
            role = random.choice(['PATIENT', 'DOCTOR'])
            user = User.objects.create_user(
                email=fake.email(),
                password='password',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=role,
                birth_date=fake.date_of_birth(minimum_age=20, maximum_age=80),
                address=fake.address(),
                phone_number=fake.phone_number()
            )
            users.append(user)
            if role == 'DOCTOR':
                DoctorProfile.objects.create(
                    user=user,
                    specialization=random.choice(DoctorProfile.SPECIALIZATIONS)[0],
                    license_number=fake.uuid4().hex[:20].upper(),
                    department=random.choice(departments),
                    qualification=fake.job(),
                    experience_years=random.randint(1, 30)
                )
            elif role == 'PATIENT':
                PatientProfile.objects.create(
                    user=user,
                    blood_group=random.choice(PatientProfile.BLOOD_GROUPS)[0],
                    emergency_contact_name=fake.name(),
                    emergency_contact_phone=fake.phone_number()
                )
        self.stdout.write(f'{len(users)} users created.')
        self.stdout.write(f'{DoctorProfile.objects.count()} doctor profiles created.')
        self.stdout.write(f'{PatientProfile.objects.count()} patient profiles created.')


        # Create Appointments
        doctors = list(DoctorProfile.objects.all())
        patients = list(PatientProfile.objects.all())

        if not doctors or not patients:
            raise CommandError("Not enough doctors or patients to create appointments. Please create more users with DOCTOR and PATIENT roles.")

        for _ in range(50):
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            appointment_date = fake.future_date(end_date='+60d')
            appointment_time = fake.time_object()

            # Basic check to avoid duplicate appointments
            if not Appointment.objects.filter(doctor=doctor, appointment_date=appointment_date, appointment_time=appointment_time).exists():
                Appointment.objects.create(
                    doctor=doctor,
                    patient=patient,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status=random.choice(['PENDING', 'CONFIRMED', 'COMPLETED']),
                    symptoms=fake.sentence()
                )
        self.stdout.write(f'{Appointment.objects.count()} appointments created.')


        # Create Bills
        for appointment in Appointment.objects.filter(status='COMPLETED'):
            if not hasattr(appointment, 'invoice'):
                Bill.objects.create(
                    patient=appointment.patient,
                    appointment=appointment,
                    subtotal=random.uniform(50.0, 500.0),
                    tax_amount=random.uniform(5.0, 50.0),
                    discount_amount=random.uniform(0.0, 20.0),
                    due_date=fake.future_date(end_date='+30d'),
                    status=random.choice(['PAID', 'UNPAID'])
                )
        self.stdout.write(f'{Bill.objects.count()} bills created.')

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))