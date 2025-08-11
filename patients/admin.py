from django.contrib import admin
from .models import PatientProfile, MedicalRecord

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'patient_id', 'email', 'phone', 'age', 'blood_group', 'created_at']
    list_filter = ['blood_group', 'created_at']
    search_fields = ['patient_id', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['patient_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'patient_id', 'blood_group')
        }),
        ('Contact Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Medical Information', {
            'fields': ('medical_history', 'current_medications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'visit_date', 'diagnosis']
    list_filter = ['visit_date', 'doctor__specialization']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'diagnosis']
    readonly_fields = ['visit_date']
    
    fieldsets = (
        ('Patient & Doctor', {
            'fields': ('patient', 'doctor')
        }),
        ('Medical Details', {
            'fields': ('diagnosis', 'treatment', 'prescription', 'notes')
        }),
        ('Appointment Details', {
            'fields': ('visit_date', 'next_appointment')
        }),
    )
