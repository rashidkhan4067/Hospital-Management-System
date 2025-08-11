from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    help = 'Create demo users for the hospital system'

    def handle(self, *args, **options):
        # Create Admin
        try:
            User.objects.get(email='admin@hospital.com')
            self.stdout.write('Admin already exists')
        except User.DoesNotExist:
            User.objects.create_superuser(email='admin@hospital.com', password='admin123', role='ADMIN')
            self.stdout.write('Admin created')

        # Create Doctor
        try:
            User.objects.get(email='doctor@hospital.com')
            self.stdout.write('Doctor already exists')
        except User.DoesNotExist:
            User.objects.create_user(email='doctor@hospital.com', password='doctor123', role='DOCTOR')
            self.stdout.write('Doctor created')

        # Create Patient
        try:
            User.objects.get(email='patient@hospital.com')
            self.stdout.write('Patient already exists')
        except User.DoesNotExist:
            User.objects.create_user(email='patient@hospital.com', password='patient123', role='PATIENT')
            self.stdout.write('Patient created')