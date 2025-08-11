#!/usr/bin/env python
"""
Test script to verify all routing fixes and functionality
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

User = get_user_model()

def test_routes():
    """Test all major routes"""
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(role='ADMIN').first()
    if not admin_user:
        print("❌ No admin user found")
        return
    
    # Login as admin
    client.force_login(admin_user)
    
    # Test routes
    routes_to_test = [
        ('/', 'Dashboard'),
        ('/patients/', 'Patients List'),
        ('/doctors/', 'Doctors List'),
        ('/appointments/', 'Appointments List'),
        ('/billing/', 'Billing List'),
        ('/analytics/', 'Analytics Dashboard'),
        ('/medical-records/', 'Medical Records List'),
    ]
    
    print("🧪 Testing Routes...")
    print("=" * 50)
    
    for url, name in routes_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name}: {url} - OK")
            elif response.status_code == 302:
                print(f"🔄 {name}: {url} - Redirect (OK)")
            else:
                print(f"❌ {name}: {url} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {url} - Error: {str(e)}")
    
    print("\n🔍 Testing Analytics Routes...")
    print("=" * 50)
    
    analytics_routes = [
        ('/analytics/', 'Analytics Dashboard'),
        ('/analytics/patients/', 'Patient Analytics'),
        ('/analytics/appointments/', 'Appointment Analytics'),
        ('/analytics/financial/', 'Financial Analytics'),
        ('/analytics/reports/', 'Reports'),
        ('/analytics/export/', 'Export Data'),
    ]
    
    for url, name in analytics_routes:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name}: {url} - OK")
            elif response.status_code == 302:
                print(f"🔄 {name}: {url} - Redirect (OK)")
            else:
                print(f"❌ {name}: {url} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {url} - Error: {str(e)}")
    
    print("\n📊 Testing Data Integrity...")
    print("=" * 50)
    
    # Test model counts
    from patients.models import PatientProfile
    from doctors.models import DoctorProfile
    from appointments.models import Appointment
    from billing.models import Bill
    from records.models import MedicalRecord
    
    print(f"👥 Patients: {PatientProfile.objects.count()}")
    print(f"👨‍⚕️ Doctors: {DoctorProfile.objects.count()}")
    print(f"📅 Appointments: {Appointment.objects.count()}")
    print(f"💰 Bills: {Bill.objects.count()}")
    print(f"📋 Medical Records: {MedicalRecord.objects.count()}")
    
    print("\n🎉 Route testing completed!")

if __name__ == '__main__':
    test_routes()
