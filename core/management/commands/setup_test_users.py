from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users for Premium HMS'

    def handle(self, *args, **options):
        # Create or update admin user
        admin_email = 'admin@premiumhms.com'
        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {admin_email}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Updated password for admin user: {admin_email}')
            )
        
        # Create test doctor user
        doctor_email = 'doctor@premiumhms.com'
        doctor_user, created = User.objects.get_or_create(
            email=doctor_email,
            defaults={
                'first_name': 'Dr. John',
                'last_name': 'Smith',
                'is_staff': True,
                'is_active': True,
            }
        )
        doctor_user.set_password('doctor123')
        doctor_user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created doctor user: {doctor_email}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Updated password for doctor user: {doctor_email}')
            )
        
        # Create test patient user
        patient_email = 'patient@premiumhms.com'
        patient_user, created = User.objects.get_or_create(
            email=patient_email,
            defaults={
                'first_name': 'Jane',
                'last_name': 'Doe',
                'is_active': True,
            }
        )
        patient_user.set_password('patient123')
        patient_user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created patient user: {patient_email}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Updated password for patient user: {patient_email}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Test Users Created ===')
        )
        self.stdout.write(f'Admin: {admin_email} / admin123')
        self.stdout.write(f'Doctor: {doctor_email} / doctor123')
        self.stdout.write(f'Patient: {patient_email} / patient123')
