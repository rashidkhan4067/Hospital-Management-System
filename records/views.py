from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import MedicalRecord
from patients.models import PatientProfile

class MedicalRecordsListView(LoginRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'records/record_list.html'
    context_object_name = 'records'
    paginate_by = 20

    def get_queryset(self):
        return MedicalRecord.objects.select_related('patient', 'doctor').order_by('-created_at')

class MedicalRecordDetailView(LoginRequiredMixin, DetailView):
    model = MedicalRecord
    template_name = 'records/record_detail.html'
    context_object_name = 'record'

class MedicalRecordCreateView(LoginRequiredMixin, CreateView):
    model = MedicalRecord
    template_name = 'records/record_form.html'
    fields = ['patient', 'doctor', 'diagnosis', 'treatment', 'medications', 'notes', 'follow_up_date']
    success_url = reverse_lazy('records:record_list')

    def form_valid(self, form):
        messages.success(self.request, 'Medical record created successfully.')
        return super().form_valid(form)

class MedicalRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = MedicalRecord
    template_name = 'records/record_form.html'
    fields = ['diagnosis', 'treatment', 'medications', 'notes', 'follow_up_date']
    success_url = reverse_lazy('records:record_list')

    def form_valid(self, form):
        messages.success(self.request, 'Medical record updated successfully.')
        return super().form_valid(form)

class MedicalRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = MedicalRecord
    template_name = 'records/record_confirm_delete.html'
    success_url = reverse_lazy('records:record_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Medical record deleted successfully.')
        return super().delete(request, *args, **kwargs)

class PatientRecordsView(LoginRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'records/patient_records.html'
    context_object_name = 'records'

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return MedicalRecord.objects.filter(patient_id=patient_id).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        context['patient'] = get_object_or_404(PatientProfile, id=patient_id)
        return context

class RecordSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'records/record_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')

        if query:
            context['records'] = MedicalRecord.objects.filter(
                diagnosis__icontains=query
            ).select_related('patient', 'doctor')[:50]
            context['query'] = query

        return context
