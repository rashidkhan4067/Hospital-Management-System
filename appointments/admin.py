from django.contrib import admin
from .models import Appointment, AppointmentHistory, Prescription

class AppointmentHistoryInline(admin.TabularInline):
    model = AppointmentHistory
    extra = 0
    readonly_fields = ['changed_at']
    can_delete = False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'appointment_id', 'patient', 'doctor', 'appointment_date', 
        'appointment_time', 'appointment_type', 'status', 'created_at'
    ]
    list_filter = [
        'status', 'appointment_type', 'appointment_date', 
        'doctor__specialization', 'created_at'
    ]
    search_fields = [
        'appointment_id', 'patient__user__first_name', 'patient__user__last_name',
        'doctor__user__first_name', 'doctor__user__last_name'
    ]
    readonly_fields = ['appointment_id', 'created_at', 'updated_at']
    inlines = [AppointmentHistoryInline]
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('appointment_id', 'patient', 'doctor', 'appointment_type')
        }),
        ('Date & Time', {
            'fields': ('appointment_date', 'appointment_time', 'duration_minutes')
        }),
        ('Status & Notes', {
            'fields': ('status', 'symptoms', 'notes', 'prescription')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'created_at', 'follow_up_date']
    search_fields = [
        'appointment__patient__user__first_name', 
        'appointment__patient__user__last_name',
        'appointment__doctor__user__first_name',
        'appointment__doctor__user__last_name'
    ]
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Appointment', {
            'fields': ('appointment',)
        }),
        ('Prescription Details', {
            'fields': ('medicines', 'tests', 'instructions')
        }),
        ('Follow-up', {
            'fields': ('follow_up_date',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at']
    readonly_fields = ['changed_at']
    search_fields = [
        'appointment__appointment_id',
        'appointment__patient__user__first_name',
        'appointment__patient__user__last_name'
    ]
