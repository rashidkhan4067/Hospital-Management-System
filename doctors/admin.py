from django.contrib import admin
from .models import Department, DoctorProfile, Schedule

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1
    min_num = 1


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'doctor_count', 'head', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    
    def doctor_count(self, obj):
        return obj.doctor_profiles.count()
    doctor_count.short_description = 'Doctors'


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'doctor_id', 'specialization', 'department', 'experience_years', 'consultation_fee', 'is_available']
    list_filter = ['specialization', 'department', 'is_available', 'experience_years']
    search_fields = ['doctor_id', 'user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['doctor_id', 'created_at', 'updated_at']
    inlines = [ScheduleInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'doctor_id', 'specialization', 'department')
        }),
        ('Professional Details', {
            'fields': ('license_number', 'experience_years', 'qualification', 'bio')
        }),
        ('Consultation Details', {
            'fields': ('consultation_fee', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_name', 'start_time', 'end_time', 'max_appointments', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'doctor__specialization']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    
    def day_name(self, obj):
        return obj.get_day_of_week_display()
    day_name.short_description = 'Day'
