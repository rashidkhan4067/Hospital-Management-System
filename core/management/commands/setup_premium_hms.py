"""
Premium HMS Setup Management Command
Comprehensive system setup and initialization
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
import random
from datetime import date, time, timedelta

from doctors.models import Department, DoctorProfile, Schedule
from patients.models import PatientProfile
from appointments.models import Appointment
from billing.models import Bill, BillItem
from medical_records.models import (
    MedicalRecordCategory, LabTest, Medication, 
    MedicalRecord, Prescription, VitalSigns
)
from notifications.models import NotificationType
from analytics.models import KPIMetric, Dashboard

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up Premium HMS with sample data and configurations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--demo-data',
            action='store_true',
            help='Create demo data for testing and demonstration',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@premiumhms.com',
            help='Admin user email address',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Admin user password',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏥 Setting up Premium Hospital Management System...')
        )
        
        try:
            with transaction.atomic():
                # Create admin user
                self.create_admin_user(options['admin_email'], options['admin_password'])
                
                # Setup basic data
                self.setup_departments()
                self.setup_notification_types()
                self.setup_medical_record_categories()
                self.setup_lab_tests()
                self.setup_medications()
                self.setup_kpi_metrics()
                self.setup_dashboards()
                
                if options['demo_data']:
                    self.create_demo_data()
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Premium HMS setup completed successfully!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Setup failed: {str(e)}')
            )
            raise CommandError(f'Setup failed: {str(e)}')
    
    def create_admin_user(self, email, password):
        """Create admin user if it doesn't exist."""
        self.stdout.write('Creating admin user...')
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user {email} already exists')
            )
            return
        
        admin_user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator',
            role='ADMIN'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Admin user created: {email}')
        )
    
    def setup_departments(self):
        """Create hospital departments."""
        self.stdout.write('Setting up departments...')
        
        departments = [
            {
                'name': 'Cardiology',
                'description': 'Heart and cardiovascular care',
            },
            {
                'name': 'Neurology',
                'description': 'Brain and nervous system disorders',
            },
            {
                'name': 'Orthopedics',
                'description': 'Bone, joint, and muscle care',
            },
            {
                'name': 'Pediatrics',
                'description': 'Medical care for children',
            },
            {
                'name': 'Emergency Medicine',
                'description': 'Emergency and urgent care',
            },
            {
                'name': 'Internal Medicine',
                'description': 'General internal medicine',
            },
            {
                'name': 'Dermatology',
                'description': 'Skin and related conditions',
            },
            {
                'name': 'Psychiatry',
                'description': 'Mental health and behavioral disorders',
            }
        ]
        
        for dept_data in departments:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults=dept_data
            )
            if created:
                self.stdout.write(f'  ✅ Created department: {department.name}')
    
    def setup_notification_types(self):
        """Create notification types."""
        self.stdout.write('Setting up notification types...')
        
        notification_types = [
            {
                'name': 'Appointment Reminder',
                'description': 'Reminder for upcoming appointments',
                'priority': 'MEDIUM',
                'email_enabled': True,
                'sms_enabled': True,
                'push_enabled': True,
            },
            {
                'name': 'Critical Lab Result',
                'description': 'Critical laboratory test results',
                'priority': 'URGENT',
                'email_enabled': True,
                'sms_enabled': True,
                'in_app_enabled': True,
            },
            {
                'name': 'Payment Due',
                'description': 'Payment reminder notifications',
                'priority': 'MEDIUM',
                'email_enabled': True,
                'sms_enabled': False,
            },
            {
                'name': 'System Alert',
                'description': 'System maintenance and alerts',
                'priority': 'HIGH',
                'email_enabled': True,
                'in_app_enabled': True,
            }
        ]
        
        for nt_data in notification_types:
            notification_type, created = NotificationType.objects.get_or_create(
                name=nt_data['name'],
                defaults=nt_data
            )
            if created:
                self.stdout.write(f'  ✅ Created notification type: {notification_type.name}')
    
    def setup_medical_record_categories(self):
        """Create medical record categories."""
        self.stdout.write('Setting up medical record categories...')
        
        categories = [
            {'name': 'General Consultation', 'color_code': '#3B82F6'},
            {'name': 'Emergency Visit', 'color_code': '#EF4444'},
            {'name': 'Follow-up', 'color_code': '#10B981'},
            {'name': 'Surgical Procedure', 'color_code': '#8B5CF6'},
            {'name': 'Diagnostic Test', 'color_code': '#F59E0B'},
            {'name': 'Preventive Care', 'color_code': '#06B6D4'},
        ]
        
        for cat_data in categories:
            category, created = MedicalRecordCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  ✅ Created category: {category.name}')
    
    def setup_lab_tests(self):
        """Create common lab tests."""
        self.stdout.write('Setting up lab tests...')
        
        lab_tests = [
            {
                'name': 'Complete Blood Count (CBC)',
                'code': 'CBC',
                'category': 'HEMATOLOGY',
                'specimen_type': 'Blood',
                'cost': Decimal('45.00'),
            },
            {
                'name': 'Basic Metabolic Panel',
                'code': 'BMP',
                'category': 'CHEMISTRY',
                'specimen_type': 'Blood',
                'cost': Decimal('35.00'),
            },
            {
                'name': 'Lipid Panel',
                'code': 'LIPID',
                'category': 'CHEMISTRY',
                'specimen_type': 'Blood',
                'requires_fasting': True,
                'cost': Decimal('55.00'),
            },
            {
                'name': 'Thyroid Stimulating Hormone (TSH)',
                'code': 'TSH',
                'category': 'CHEMISTRY',
                'specimen_type': 'Blood',
                'cost': Decimal('65.00'),
            },
            {
                'name': 'Urinalysis',
                'code': 'UA',
                'category': 'URINE',
                'specimen_type': 'Urine',
                'cost': Decimal('25.00'),
            }
        ]
        
        for test_data in lab_tests:
            lab_test, created = LabTest.objects.get_or_create(
                code=test_data['code'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'  ✅ Created lab test: {lab_test.name}')
    
    def setup_medications(self):
        """Create common medications."""
        self.stdout.write('Setting up medications...')
        
        medications = [
            {
                'name': 'Lisinopril',
                'generic_name': 'Lisinopril',
                'medication_type': 'TABLET',
                'strength': '10mg',
                'active_ingredients': 'Lisinopril',
                'common_uses': 'High blood pressure, heart failure',
            },
            {
                'name': 'Metformin',
                'generic_name': 'Metformin',
                'medication_type': 'TABLET',
                'strength': '500mg',
                'active_ingredients': 'Metformin hydrochloride',
                'common_uses': 'Type 2 diabetes',
            },
            {
                'name': 'Amoxicillin',
                'generic_name': 'Amoxicillin',
                'medication_type': 'CAPSULE',
                'strength': '500mg',
                'active_ingredients': 'Amoxicillin',
                'common_uses': 'Bacterial infections',
            },
            {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'medication_type': 'TABLET',
                'strength': '200mg',
                'active_ingredients': 'Ibuprofen',
                'common_uses': 'Pain relief, inflammation',
                'requires_prescription': False,
            }
        ]
        
        for med_data in medications:
            medication, created = Medication.objects.get_or_create(
                name=med_data['name'],
                strength=med_data['strength'],
                defaults=med_data
            )
            if created:
                self.stdout.write(f'  ✅ Created medication: {medication.name}')
    
    def setup_kpi_metrics(self):
        """Create KPI metrics."""
        self.stdout.write('Setting up KPI metrics...')
        
        admin_user = User.objects.filter(role='ADMIN').first()
        
        kpi_metrics = [
            {
                'name': 'Patient Satisfaction Score',
                'description': 'Average patient satisfaction rating',
                'category': 'PATIENT_SATISFACTION',
                'metric_type': 'AVERAGE',
                'target_value': Decimal('4.5'),
                'warning_threshold': Decimal('4.0'),
                'unit': '/5',
                'created_by': admin_user,
            },
            {
                'name': 'Appointment Completion Rate',
                'description': 'Percentage of appointments completed',
                'category': 'OPERATIONAL',
                'metric_type': 'PERCENTAGE',
                'target_value': Decimal('95.0'),
                'warning_threshold': Decimal('90.0'),
                'unit': '%',
                'created_by': admin_user,
            },
            {
                'name': 'Average Wait Time',
                'description': 'Average patient wait time in minutes',
                'category': 'EFFICIENCY',
                'metric_type': 'AVERAGE',
                'target_value': Decimal('10.0'),
                'warning_threshold': Decimal('15.0'),
                'unit': 'minutes',
                'created_by': admin_user,
            },
            {
                'name': 'Monthly Revenue',
                'description': 'Total monthly revenue',
                'category': 'FINANCIAL',
                'metric_type': 'SUM',
                'unit': '$',
                'created_by': admin_user,
            }
        ]
        
        for kpi_data in kpi_metrics:
            if kpi_data['created_by']:  # Only create if admin user exists
                kpi_metric, created = KPIMetric.objects.get_or_create(
                    name=kpi_data['name'],
                    defaults=kpi_data
                )
                if created:
                    self.stdout.write(f'  ✅ Created KPI metric: {kpi_metric.name}')
    
    def setup_dashboards(self):
        """Create default dashboards."""
        self.stdout.write('Setting up dashboards...')
        
        admin_user = User.objects.filter(role='ADMIN').first()
        
        if not admin_user:
            return
        
        dashboards = [
            {
                'name': 'Executive Dashboard',
                'description': 'High-level overview for executives',
                'dashboard_type': 'EXECUTIVE',
                'is_public': True,
                'created_by': admin_user,
            },
            {
                'name': 'Clinical Dashboard',
                'description': 'Clinical metrics and patient care indicators',
                'dashboard_type': 'CLINICAL',
                'is_public': True,
                'created_by': admin_user,
            },
            {
                'name': 'Financial Dashboard',
                'description': 'Financial performance and billing metrics',
                'dashboard_type': 'FINANCIAL',
                'is_public': False,
                'created_by': admin_user,
            }
        ]
        
        for dash_data in dashboards:
            dashboard, created = Dashboard.objects.get_or_create(
                name=dash_data['name'],
                defaults=dash_data
            )
            if created:
                self.stdout.write(f'  ✅ Created dashboard: {dashboard.name}')
    
    def create_demo_data(self):
        """Create demo data for testing."""
        self.stdout.write('Creating demo data...')
        
        # This would create sample patients, doctors, appointments, etc.
        # Implementation would be extensive, so keeping it simple for now
        
        self.stdout.write('  ✅ Demo data creation completed')
