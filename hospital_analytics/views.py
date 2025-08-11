from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, date
from patients.models import PatientProfile
from appointments.models import Appointment
from billing.models import Bill
from doctors.models import DoctorProfile
from records.models import MedicalRecord
import json

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date ranges
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)

        # Basic statistics
        context['total_patients'] = PatientProfile.objects.count()
        context['total_doctors'] = DoctorProfile.objects.count()
        context['total_appointments'] = Appointment.objects.count()
        context['total_revenue'] = Bill.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['total_records'] = MedicalRecord.objects.count()

        # Recent data (last 30 days)
        context['recent_patients'] = PatientProfile.objects.filter(created_at__gte=thirty_days_ago).count()
        context['recent_appointments'] = Appointment.objects.filter(created_at__gte=thirty_days_ago).count()
        context['recent_records'] = MedicalRecord.objects.filter(created_at__gte=thirty_days_ago).count()

        # Weekly data for charts
        context['weekly_appointments'] = self.get_weekly_appointments()
        context['monthly_revenue'] = self.get_monthly_revenue()
        context['appointment_status_data'] = self.get_appointment_status_data()
        context['patient_growth_data'] = self.get_patient_growth_data()

        return context

    def get_weekly_appointments(self):
        """Get appointments for the last 7 days"""
        data = []
        labels = []

        for i in range(7):
            day = timezone.now().date() - timedelta(days=6-i)
            count = Appointment.objects.filter(appointment_date=day).count()
            data.append(count)
            labels.append(day.strftime('%a'))

        return {
            'labels': labels,
            'data': data
        }

    def get_monthly_revenue(self):
        """Get revenue for the last 6 months"""
        data = []
        labels = []

        for i in range(6):
            month_start = (timezone.now().date().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            revenue = Bill.objects.filter(
                created_at__date__gte=month_start,
                created_at__date__lte=month_end,
                status='PAID'
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

            data.insert(0, float(revenue))
            labels.insert(0, month_start.strftime('%b'))

        return {
            'labels': labels,
            'data': data
        }

    def get_appointment_status_data(self):
        """Get appointment status distribution"""
        status_data = Appointment.objects.values('status').annotate(count=Count('id'))

        labels = []
        data = []
        colors = {
            'PENDING': '#ffc107',
            'CONFIRMED': '#28a745',
            'COMPLETED': '#007bff',
            'CANCELLED': '#dc3545',
            'NO_SHOW': '#6c757d'
        }

        for item in status_data:
            labels.append(item['status'])
            data.append(item['count'])

        return {
            'labels': labels,
            'data': data,
            'colors': [colors.get(label, '#6c757d') for label in labels]
        }

    def get_patient_growth_data(self):
        """Get patient growth over the last 12 months"""
        data = []
        labels = []

        for i in range(12):
            month_start = (timezone.now().date().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            count = PatientProfile.objects.filter(
                created_at__date__gte=month_start,
                created_at__date__lte=month_end
            ).count()

            data.insert(0, count)
            labels.insert(0, month_start.strftime('%b'))

        return {
            'labels': labels,
            'data': data
        }

class PatientAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/patient_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Patient demographics
        context['gender_distribution'] = PatientProfile.objects.values('gender').annotate(count=Count('id'))
        context['age_groups'] = self.get_age_groups()

        return context

    def get_age_groups(self):
        # Simple age grouping logic
        patients = PatientProfile.objects.all()
        age_groups = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}

        for patient in patients:
            if patient.date_of_birth:
                age = (timezone.now().date() - patient.date_of_birth).days // 365
                if age <= 18:
                    age_groups['0-18'] += 1
                elif age <= 35:
                    age_groups['19-35'] += 1
                elif age <= 50:
                    age_groups['36-50'] += 1
                elif age <= 65:
                    age_groups['51-65'] += 1
                else:
                    age_groups['65+'] += 1

        return age_groups

class AppointmentAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/appointment_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Appointment statistics
        context['status_distribution'] = Appointment.objects.values('status').annotate(count=Count('id'))
        context['monthly_appointments'] = self.get_monthly_appointments()

        return context

    def get_monthly_appointments(self):
        # Get appointments for the last 12 months
        twelve_months_ago = timezone.now() - timedelta(days=365)
        appointments = Appointment.objects.filter(created_at__gte=twelve_months_ago)

        monthly_data = {}
        for appointment in appointments:
            month_key = appointment.created_at.strftime('%Y-%m')
            monthly_data[month_key] = monthly_data.get(month_key, 0) + 1

        return monthly_data

class FinancialAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/financial_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Financial statistics
        context['total_revenue'] = Bill.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['average_bill'] = Bill.objects.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        context['payment_status'] = Bill.objects.values('status').annotate(count=Count('id'))

        return context

class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/reports.html'

class ExportDataView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/export.html'
