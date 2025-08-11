from django.db import models
from django.conf import settings
import uuid

class Service(models.Model):
    """Hospital services and their charges"""
    
    SERVICE_TYPES = [
        ('CONSULTATION', 'Consultation'),
        ('LAB_TEST', 'Lab Test'),
        ('XRAY', 'X-Ray'),
        ('ULTRASOUND', 'Ultrasound'),
        ('ECG', 'ECG'),
        ('BLOOD_TEST', 'Blood Test'),
        ('SURGERY', 'Surgery'),
        ('ROOM_CHARGE', 'Room Charge'),
        ('MEDICINE', 'Medicine'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['service_type', 'name']
    
    def __str__(self):
        return f"{self.name} - ${self.base_price}"


class Bill(models.Model):
    """Patient invoices/bills"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('INSURANCE', 'Insurance'),
        ('CHEQUE', 'Cheque'),
    ]
    
    bill_number = models.CharField(max_length=12, unique=True, editable=False)
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='invoice',
        null=True,
        blank=True
    )
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bill_number']),
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.bill_number} - {self.patient.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate unique bill number
            self.bill_number = f"BILL{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate totals
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        super().save(*args, **kwargs)
    
    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_paid(self):
        return self.paid_amount >= self.total_amount
    
    @property
    def is_overdue(self):
        from datetime import date
        return date.today() > self.due_date and not self.is_paid


class BillItem(models.Model):
    """Individual items in an invoice"""
    
    bill = models.ForeignKey(
        'Bill',
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='invoice_items'
    )
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['service__name']
    
    def __str__(self):
        return f"{self.bill.bill_number} - {self.service.name}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records for invoices"""
    
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('INSURANCE', 'Insurance'),
        ('CHEQUE', 'Cheque'),
    ]
    
    payment_id = models.CharField(max_length=12, unique=True, editable=False)
    invoice = models.ForeignKey(
        'Bill',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    payment_date = models.DateField()
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.payment_id} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate unique payment ID
            self.payment_id = f"PAY{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Insurance(models.Model):
    """Patient insurance information"""
    
    INSURANCE_TYPES = [
        ('HEALTH', 'Health Insurance'),
        ('DENTAL', 'Dental Insurance'),
        ('VISION', 'Vision Insurance'),
    ]
    
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='insurance_policies'
    )
    provider_name = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=50)
    insurance_type = models.CharField(max_length=10, choices=INSURANCE_TYPES)
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.provider_name}"
    
    @property
    def is_expired(self):
        from datetime import date
        return date.today() > self.expiry_date
