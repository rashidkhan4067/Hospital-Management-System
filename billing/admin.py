from django.contrib import admin
from .models import Service, Bill, BillItem, Payment, Insurance

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1
    fields = ['service', 'description', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['amount', 'payment_method', 'payment_date', 'transaction_id']
    readonly_fields = ['payment_id']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'base_price', 'is_active', 'created_at']
    list_filter = ['service_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Service Details', {
            'fields': ('name', 'service_type', 'description', 'base_price')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = [
        'bill_number', 'patient', 'issue_date', 'due_date', 
        'total_amount', 'paid_amount', 'balance_due', 'status'
    ]
    list_filter = ['status', 'issue_date', 'due_date', 'payment_method']
    search_fields = [
        'bill_number', 'patient__user__first_name', 
        'patient__user__last_name', 'patient__patient_id'
    ]
    readonly_fields = ['bill_number', 'created_at', 'updated_at']
    inlines = [BillItemInline, PaymentInline]
    
    fieldsets = (
        ('Bill Details', {
            'fields': ('bill_number', 'patient', 'appointment')
        }),
        ('Amount Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount')
        }),
        ('Payment Details', {
            'fields': ('status', 'payment_method', 'due_date')
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('issue_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def balance_due(self, obj):
        return obj.balance_due
    balance_due.short_description = 'Balance Due'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'invoice', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_id', 'invoice__bill_number', 'transaction_id']
    readonly_fields = ['payment_id', 'created_at']
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('payment_id', 'invoice', 'amount', 'payment_method')
        }),
        ('Transaction Details', {
            'fields': ('payment_date', 'transaction_id', 'notes')
        }),
        ('Staff', {
            'fields': ('received_by',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['patient', 'provider_name', 'policy_number', 'coverage_amount', 'expiry_date', 'is_active']
    list_filter = ['insurance_type', 'is_active', 'expiry_date']
    search_fields = [
        'patient__user__first_name', 'patient__user__last_name',
        'provider_name', 'policy_number'
    ]
    
    fieldsets = (
        ('Patient', {
            'fields': ('patient',)
        }),
        ('Policy Details', {
            'fields': ('provider_name', 'policy_number', 'insurance_type', 'coverage_amount')
        }),
        ('Validity', {
            'fields': ('expiry_date', 'is_active')
        }),
    )
