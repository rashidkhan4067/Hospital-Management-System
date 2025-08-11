from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, CreateView
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User
from .forms import CustomUserCreationForm, UserProfileForm

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/premium_dashboard.html'
    login_url = reverse_lazy('core:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.role == 'ADMIN':
            from patients.models import PatientProfile
            from doctors.models import DoctorProfile
            from appointments.models import Appointment
            from billing.models import Bill
            from records.models import MedicalRecord

            # Get date ranges
            today = timezone.now().date()
            thirty_days_ago = today - timedelta(days=30)

            # Admin dashboard statistics
            context.update({
                'total_patients': PatientProfile.objects.count(),
                'total_doctors': DoctorProfile.objects.count(),
                'total_appointments': Appointment.objects.count(),
                'total_medical_records': MedicalRecord.objects.count(),
                'today_appointments': Appointment.objects.filter(
                    appointment_date=today
                ).count(),
                'pending_appointments': Appointment.objects.filter(
                    status='PENDING'
                ).count(),
                'total_revenue': Bill.objects.filter(
                    status='PAID'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'recent_patients': PatientProfile.objects.filter(
                    created_at__gte=thirty_days_ago
                ).count(),
                'recent_appointments': Appointment.objects.select_related(
                    'patient', 'doctor'
                ).order_by('-created_at')[:10],
                'recent_invoices': Bill.objects.select_related(
                    'patient'
                ).order_by('-created_at')[:10],
                'recent_records': MedicalRecord.objects.select_related(
                    'patient', 'doctor'
                ).order_by('-created_at')[:5],
                'appointment_trends': self.get_appointment_trends(),
                'weekly_stats': self.get_weekly_stats(),
            })

        elif self.request.user.role == 'DOCTOR':
            from appointments.models import Appointment

            # Doctor dashboard
            doctor = self.request.user.doctor_profile
            context.update({
                'today_appointments': Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=timezone.now().date(),
                    status__in=['CONFIRMED', 'PENDING']
                ).count(),
                'total_appointments': Appointment.objects.filter(
                    doctor=doctor
                ).count(),
                'recent_appointments': Appointment.objects.filter(
                    doctor=doctor
                ).order_by('-created_at')[:10],
            })

        return context

    def get_appointment_trends(self):
        """Get appointment trends for the last 7 days"""
        from appointments.models import Appointment

        trends = {
            'labels': [],
            'data': []
        }

        for i in range(7):
            day = timezone.now().date() - timedelta(days=6-i)
            count = Appointment.objects.filter(appointment_date=day).count()
            trends['labels'].append(day.strftime('%a'))
            trends['data'].append(count)

        return trends

    def get_weekly_stats(self):
        """Get weekly statistics"""
        from appointments.models import Appointment
        from billing.models import Bill

        week_start = timezone.now().date() - timedelta(days=7)

        return {
            'appointments_this_week': Appointment.objects.filter(
                appointment_date__gte=week_start
            ).count(),
            'revenue_this_week': Bill.objects.filter(
                created_at__date__gte=week_start,
                status='PAID'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
        }


class LoginView(TemplateView):
    template_name = 'registration/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        from django.contrib.auth import authenticate
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
            
            # Redirect based on role
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, self.template_name)


class TestView(TemplateView):
    template_name = 'core/test.html'

class CSSTestView(TemplateView):
    template_name = 'core/css_test.html'

class CustomLoginView(TemplateView):
    template_name = 'registration/premium_login.html'

    def get(self, request, *args, **kwargs):
        # If user is already logged in, redirect to dashboard
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import authenticate

        email = request.POST.get('email')  # Use email as username
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, self.template_name)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')

                # Redirect based on role or next parameter
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Your account is disabled. Please contact administrator.')
                return render(request, self.template_name)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
            return render(request, self.template_name)


class LogoutView(LogoutView):
    next_page = 'core:login'


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('core:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.role == 'PATIENT':
            from patients.models import PatientProfile
            try:
                context['profile'] = self.request.user.patient_profile
            except AttributeError:
                context['profile'] = None
            
        elif self.request.user.role == 'DOCTOR':
            from doctors.models import DoctorProfile
            context['profile'] = self.request.user.doctor_profile
            
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'core/profile_edit.html'
    success_url = reverse_lazy('core:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
