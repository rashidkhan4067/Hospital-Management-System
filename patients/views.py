from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import PatientProfile, MedicalRecord
from .forms import PatientProfileForm, MedicalRecordForm, PatientEditForm, PatientUserForm
from core.models import User

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ADMIN'

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'DOCTOR']

class PatientListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = PatientProfile
    template_name = 'patients/premium_patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(patient_id__icontains=search) |
                Q(user__email__icontains=search)
            )
        return queryset.select_related('user')


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'patients/premium_patient_detail.html'
    context_object_name = 'patient'
    
    def get_queryset(self):
        return super().get_queryset().select_related('user')


class PatientCreateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'patients/patient_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .forms import PatientUserForm
        context['user_form'] = PatientUserForm()
        context['profile_form'] = PatientProfileForm()
        return context

    def post(self, request, *args, **kwargs):
        from .forms import PatientUserForm
        user_form = PatientUserForm(request.POST)
        profile_form = PatientProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Create user
            user = user_form.save()

            # Create patient profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, f'Patient {user.get_full_name()} created successfully!')
            return redirect('patients:patient_list')
        else:
            context = self.get_context_data()
            context['user_form'] = user_form
            context['profile_form'] = profile_form
            return self.render_to_response(context)


class PatientUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = PatientProfile
    template_name = 'patients/patient_edit.html'
    success_url = reverse_lazy('patients:patient_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = PatientEditForm(self.request.POST, instance=self.object.user)
            context['profile_form'] = PatientProfileForm(self.request.POST, instance=self.object)
        else:
            context['user_form'] = PatientEditForm(instance=self.object.user)
            context['profile_form'] = PatientProfileForm(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        profile_form = context['profile_form']

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(self.request, 'Patient updated successfully.')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        messages.success(self.request, 'Patient updated successfully!')
        return super().form_valid(form)


class MedicalRecordListView(LoginRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'patients/medical_record_list.html'
    context_object_name = 'records'
    paginate_by = 10

    def get_queryset(self):
        self.patient = get_object_or_404(PatientProfile, pk=self.kwargs['pk'])
        return MedicalRecord.objects.filter(
            patient=self.patient
        ).select_related('patient', 'doctor__user').order_by('-visit_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.patient
        return context


class MedicalRecordCreateView(LoginRequiredMixin, DoctorRequiredMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'patients/medical_record_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(PatientProfile, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        patient = get_object_or_404(PatientProfile, pk=self.kwargs['pk'])
        form.instance.patient = patient
        form.instance.doctor = self.request.user.doctor_profile
        messages.success(self.request, 'Medical record added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('patients:patient_records', kwargs={'pk': self.kwargs['pk']})


class PatientSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'patients/patient_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        patients = []

        if query:
            patients = PatientProfile.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(patient_id__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__phone_number__icontains=query)
            ).select_related('user')[:20]

        context['query'] = query
        context['patients'] = patients
        return context


class PatientSearchView(LoginRequiredMixin, ListView):
    model = PatientProfile
    template_name = 'patients/patient_search.html'
    context_object_name = 'patients'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return PatientProfile.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(patient_id__icontains=query) |
                Q(user__email__icontains=query) |
                Q(user__phone_number__icontains=query)
            ).select_related('user')
        return PatientProfile.objects.none()
