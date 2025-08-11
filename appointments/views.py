from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from .forms import AppointmentForm, BookAppointmentForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ADMIN'

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'DOCTOR']

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter based on user role
        if self.request.user.role == 'PATIENT':
            queryset = queryset.filter(patient=self.request.user.patient_profile)
        elif self.request.user.role == 'DOCTOR':
            queryset = queryset.filter(doctor=self.request.user.doctor_profile)
        
        # Search and filter
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if search:
            queryset = queryset.filter(
                Q(patient__user__first_name__icontains=search) |
                Q(patient__user__last_name__icontains=search) |
                Q(doctor__user__first_name__icontains=search) |
                Q(doctor__user__last_name__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
            
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        
        return queryset.select_related('patient__user', 'doctor__user').order_by('-appointment_date', '-appointment_time')


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient__user', 'doctor__user')


class AppointmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/premium_appointment_create.html'
    success_url = reverse_lazy('appointments:appointment_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Appointment created successfully!')
        return super().form_valid(form)


class AppointmentUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointments:appointment_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Appointment updated successfully!')
        return super().form_valid(form)


class AppointmentCancelView(LoginRequiredMixin, UpdateView):
    model = Appointment
    fields = ['status']
    template_name = 'appointments/appointment_cancel.html'
    
    def form_valid(self, form):
        form.instance.status = 'CANCELLED'
        messages.success(self.request, 'Appointment cancelled successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('appointments:appointment_detail', kwargs={'pk': self.object.pk})


class AppointmentConfirmView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Appointment
    fields = ['status']
    template_name = 'appointments/appointment_confirm.html'
    
    def form_valid(self, form):
        form.instance.status = 'CONFIRMED'
        messages.success(self.request, 'Appointment confirmed successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('appointments:appointment_detail', kwargs={'pk': self.object.pk})


class AppointmentCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'appointments/appointment_calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date
        today = timezone.now().date()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        
        # Get appointments for the week
        appointments = Appointment.objects.filter(
            appointment_date__range=[start_date, end_date]
        ).select_related('patient__user', 'doctor__user').order_by('appointment_date', 'appointment_time')
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'appointments': appointments,
        })
        return context


class BookAppointmentView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = BookAppointmentForm
    template_name = 'appointments/book_appointment.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        if self.request.user.role == 'PATIENT':
            form.instance.patient = self.request.user.patient_profile
        messages.success(self.request, 'Appointment booked successfully! Please wait for confirmation.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('appointments:my_appointments')


class MyAppointmentsView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/my_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        if self.request.user.role == 'PATIENT':
            return Appointment.objects.filter(
                patient=self.request.user.patient_profile
            ).select_related('doctor__user').order_by('-appointment_date', '-appointment_time')
        elif self.request.user.role == 'DOCTOR':
            return Appointment.objects.filter(
                doctor=self.request.user.doctor_profile
            ).select_related('patient__user').order_by('-appointment_date', '-appointment_time')
        return Appointment.objects.none()


class AppointmentConfirmView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.status = 'CONFIRMED'
        appointment.save()
        messages.success(request, f'Appointment {appointment.appointment_id} confirmed successfully!')
        return redirect('appointments:appointment_detail', pk=pk)


class AppointmentCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        # Check permissions
        if (request.user.role == 'ADMIN' or
            (request.user.role == 'PATIENT' and appointment.patient.user == request.user) or
            (request.user.role == 'DOCTOR' and appointment.doctor.user == request.user)):

            appointment.status = 'CANCELLED'
            appointment.save()
            messages.success(request, f'Appointment {appointment.appointment_id} cancelled successfully!')
        else:
            messages.error(request, 'You do not have permission to cancel this appointment.')

        return redirect('appointments:appointment_detail', pk=pk)
