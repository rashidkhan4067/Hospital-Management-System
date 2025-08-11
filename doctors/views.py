from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count
from .models import DoctorProfile, Department, Schedule
from .forms import DoctorProfileForm, ScheduleForm, DoctorUserForm, DoctorEditForm
from core.models import User

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ADMIN'

class DoctorListView(LoginRequiredMixin, ListView):
    model = DoctorProfile
    template_name = 'doctors/premium_doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        specialization = self.request.GET.get('specialization')
        
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(specialization__icontains=search) |
                Q(doctor_id__icontains=search)
            )
        
        if department:
            queryset = queryset.filter(department_id=department)
            
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        
        return queryset.select_related('user', 'department').filter(is_available=True)


class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = DoctorProfile
    template_name = 'doctors/premium_doctor_detail.html'
    context_object_name = 'doctor'
    
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'department')


class DoctorCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'doctors/doctor_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = DoctorUserForm()
        context['profile_form'] = DoctorProfileForm()
        context['departments'] = Department.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        user_form = DoctorUserForm(request.POST)
        profile_form = DoctorProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Create user
            user = user_form.save()

            # Create doctor profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, f'Doctor {user.get_full_name()} created successfully!')
            return redirect('doctors:doctor_list')
        else:
            context = self.get_context_data()
            context['user_form'] = user_form
            context['profile_form'] = profile_form
            return self.render_to_response(context)


class DoctorUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = DoctorProfile
    template_name = 'doctors/doctor_edit.html'
    success_url = reverse_lazy('doctors:doctor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = DoctorEditForm(self.request.POST, instance=self.object.user)
            context['profile_form'] = DoctorProfileForm(self.request.POST, instance=self.object)
        else:
            context['user_form'] = DoctorEditForm(instance=self.object.user)
            context['profile_form'] = DoctorProfileForm(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        profile_form = context['profile_form']

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(self.request, 'Doctor updated successfully.')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        messages.success(self.request, 'Doctor profile updated successfully!')
        return super().form_valid(form)


class DoctorScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'doctors/doctor_schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_object_or_404(DoctorProfile, pk=self.kwargs['pk'])
        
        # Get schedule for the doctor
        schedule = Schedule.objects.filter(
            doctor=doctor,
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        context.update({
            'doctor': doctor,
            'schedule': schedule,
            'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        })
        return context


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'doctors/department_list.html'
    context_object_name = 'departments'
    
    def get_queryset(self):
        return super().get_queryset().annotate(
            doctor_count=Count('doctor_profiles')
        )


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'doctors/department_detail.html'
    context_object_name = 'department'
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('doctor_profiles__user')


class DoctorSearchView(LoginRequiredMixin, ListView):
    model = DoctorProfile
    template_name = 'doctors/doctor_search.html'
    context_object_name = 'doctors'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return DoctorProfile.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(specialization__icontains=query) |
                Q(department__name__icontains=query)
            ).select_related('user', 'department').filter(is_available=True)
        return DoctorProfile.objects.select_related('user', 'department').filter(is_available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        return context
