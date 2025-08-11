"""
Premium HMS Medical Records Models
Advanced medical record management with comprehensive tracking
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class MedicalRecordCategory(models.Model):
    """Categories for organizing medical records."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Medical Record Categories'
    
    def __str__(self):
        return self.name


class MedicalRecord(models.Model):
    """Enhanced medical records with comprehensive tracking."""
    
    RECORD_TYPES = [
        ('CONSULTATION', 'Consultation'),
        ('DIAGNOSIS', 'Diagnosis'),
        ('TREATMENT', 'Treatment'),
        ('SURGERY', 'Surgery'),
        ('EMERGENCY', 'Emergency'),
        ('FOLLOW_UP', 'Follow-up'),
        ('PREVENTIVE', 'Preventive Care'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
        ('CRITICAL', 'Critical'),
    ]
    
    record_id = models.CharField(max_length=12, unique=True, editable=False)
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='enhanced_medical_records'
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='enhanced_medical_records'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_records'
    )
    
    # Record details
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='CONSULTATION')
    category = models.ForeignKey(MedicalRecordCategory, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')
    
    # Medical information
    chief_complaint = models.TextField(help_text="Patient's main concern or reason for visit")
    history_of_present_illness = models.TextField(blank=True)
    physical_examination = models.TextField(blank=True)
    assessment = models.TextField(help_text="Doctor's assessment and diagnosis")
    plan = models.TextField(help_text="Treatment plan and recommendations")
    
    # Additional fields
    notes = models.TextField(blank=True, help_text="Additional notes and observations")
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    visit_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    is_confidential = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['patient', '-visit_date']),
            models.Index(fields=['doctor', '-visit_date']),
            models.Index(fields=['record_type']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.record_id} - {self.patient.full_name} ({self.visit_date.date()})"
    
    def save(self, *args, **kwargs):
        if not self.record_id:
            self.record_id = f"MR{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Prescription(models.Model):
    """Prescription management with detailed medication tracking."""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DISCONTINUED', 'Discontinued'),
        ('EXPIRED', 'Expired'),
    ]
    
    prescription_id = models.CharField(max_length=12, unique=True, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    
    # Prescription details
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    prescribed_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Instructions
    general_instructions = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    
    # Metadata
    is_controlled_substance = models.BooleanField(default=False)
    refills_allowed = models.PositiveIntegerField(default=0)
    refills_used = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prescribed_date']
        indexes = [
            models.Index(fields=['patient', '-prescribed_date']),
            models.Index(fields=['doctor', '-prescribed_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.prescription_id} - {self.patient.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.prescription_id:
            self.prescription_id = f"RX{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if prescription has expired."""
        if self.end_date:
            return timezone.now().date() > self.end_date
        return False
    
    @property
    def refills_remaining(self):
        """Calculate remaining refills."""
        return max(0, self.refills_allowed - self.refills_used)


class Medication(models.Model):
    """Medication database with comprehensive drug information."""
    
    MEDICATION_TYPES = [
        ('TABLET', 'Tablet'),
        ('CAPSULE', 'Capsule'),
        ('LIQUID', 'Liquid'),
        ('INJECTION', 'Injection'),
        ('TOPICAL', 'Topical'),
        ('INHALER', 'Inhaler'),
        ('DROPS', 'Drops'),
        ('PATCH', 'Patch'),
    ]
    
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_names = models.TextField(blank=True, help_text="Comma-separated brand names")
    medication_type = models.CharField(max_length=20, choices=MEDICATION_TYPES)
    
    # Drug information
    strength = models.CharField(max_length=50, help_text="e.g., 500mg, 10ml")
    active_ingredients = models.TextField()
    description = models.TextField(blank=True)
    
    # Usage information
    common_uses = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    drug_interactions = models.TextField(blank=True)
    
    # Regulatory information
    is_controlled_substance = models.BooleanField(default=False)
    requires_prescription = models.BooleanField(default=True)
    fda_approved = models.BooleanField(default=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['generic_name']),
            models.Index(fields=['medication_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.strength})"


class PrescriptionMedication(models.Model):
    """Junction table for prescription medications with dosage details."""
    
    FREQUENCY_CHOICES = [
        ('ONCE_DAILY', 'Once daily'),
        ('TWICE_DAILY', 'Twice daily'),
        ('THREE_TIMES_DAILY', 'Three times daily'),
        ('FOUR_TIMES_DAILY', 'Four times daily'),
        ('EVERY_4_HOURS', 'Every 4 hours'),
        ('EVERY_6_HOURS', 'Every 6 hours'),
        ('EVERY_8_HOURS', 'Every 8 hours'),
        ('EVERY_12_HOURS', 'Every 12 hours'),
        ('AS_NEEDED', 'As needed'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medications'
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    
    # Dosage information
    dosage = models.CharField(max_length=100, help_text="e.g., 1 tablet, 5ml")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Instructions
    instructions = models.TextField(blank=True, help_text="Specific instructions for this medication")
    take_with_food = models.BooleanField(default=False)
    
    # Quantity
    quantity_prescribed = models.PositiveIntegerField(help_text="Total quantity prescribed")
    quantity_dispensed = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['prescription', 'medication']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.medication.name} - {self.dosage} {self.frequency}"


class VitalSigns(models.Model):
    """Patient vital signs tracking."""
    
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='vital_signs'
    )
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='vital_signs'
    )
    
    # Vital measurements
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(90.0), MaxValueValidator(110.0)],
        help_text="Temperature in Fahrenheit"
    )
    blood_pressure_systolic = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(300)]
    )
    blood_pressure_diastolic = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(200)]
    )
    heart_rate = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(250)],
        help_text="Beats per minute"
    )
    respiratory_rate = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        help_text="Breaths per minute"
    )
    oxygen_saturation = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(70), MaxValueValidator(100)],
        help_text="Oxygen saturation percentage"
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(999.9)],
        help_text="Weight in pounds"
    )
    height = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(10), MaxValueValidator(120)],
        help_text="Height in inches"
    )
    
    # Additional measurements
    pain_scale = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Pain scale 0-10"
    )
    
    # Metadata
    measured_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_vitals'
    )
    measured_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['patient', '-measured_at']),
            models.Index(fields=['medical_record']),
        ]
    
    def __str__(self):
        return f"Vitals for {self.patient.full_name} - {self.measured_at.date()}"
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight are available."""
        if self.height and self.weight:
            height_meters = float(self.height) * 0.0254  # inches to meters
            weight_kg = float(self.weight) * 0.453592  # pounds to kg
            return round(weight_kg / (height_meters ** 2), 1)
        return None
    
    @property
    def blood_pressure(self):
        """Return formatted blood pressure."""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None


class LabTest(models.Model):
    """Laboratory test definitions."""

    TEST_CATEGORIES = [
        ('BLOOD', 'Blood Tests'),
        ('URINE', 'Urine Tests'),
        ('STOOL', 'Stool Tests'),
        ('MICROBIOLOGY', 'Microbiology'),
        ('CHEMISTRY', 'Clinical Chemistry'),
        ('HEMATOLOGY', 'Hematology'),
        ('IMMUNOLOGY', 'Immunology'),
        ('PATHOLOGY', 'Pathology'),
        ('GENETICS', 'Genetic Testing'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=TEST_CATEGORIES)
    description = models.TextField(blank=True)

    # Reference values
    reference_range_min = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    reference_range_max = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    reference_range_text = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, blank=True)

    # Test information
    specimen_type = models.CharField(max_length=100, blank=True)
    preparation_instructions = models.TextField(blank=True)
    turnaround_time_hours = models.PositiveIntegerField(default=24)

    # Pricing
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # Metadata
    is_active = models.BooleanField(default=True)
    requires_fasting = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class LabOrder(models.Model):
    """Laboratory test orders."""

    STATUS_CHOICES = [
        ('ORDERED', 'Ordered'),
        ('COLLECTED', 'Sample Collected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PRIORITY_LEVELS = [
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
        ('STAT', 'STAT'),
    ]

    order_id = models.CharField(max_length=12, unique=True, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='lab_orders'
    )
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='lab_orders'
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='lab_orders'
    )

    # Order details
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ORDERED')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='ROUTINE')

    # Instructions
    clinical_notes = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)

    # Timestamps
    ordered_at = models.DateTimeField(default=timezone.now)
    collected_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Staff
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collected_lab_orders'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ordered_at']
        indexes = [
            models.Index(fields=['patient', '-ordered_at']),
            models.Index(fields=['doctor', '-ordered_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.order_id} - {self.patient.full_name}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"LAB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class LabOrderTest(models.Model):
    """Individual tests within a lab order."""

    lab_order = models.ForeignKey(
        LabOrder,
        on_delete=models.CASCADE,
        related_name='tests'
    )
    lab_test = models.ForeignKey(
        LabTest,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # Test-specific instructions
    instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['lab_order', 'lab_test']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.lab_order.order_id} - {self.lab_test.name}"


class LabResult(models.Model):
    """Laboratory test results."""

    RESULT_STATUS = [
        ('PENDING', 'Pending'),
        ('PRELIMINARY', 'Preliminary'),
        ('FINAL', 'Final'),
        ('CORRECTED', 'Corrected'),
        ('CANCELLED', 'Cancelled'),
    ]

    ABNORMAL_FLAGS = [
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('LOW', 'Low'),
        ('CRITICAL_HIGH', 'Critical High'),
        ('CRITICAL_LOW', 'Critical Low'),
        ('ABNORMAL', 'Abnormal'),
    ]

    result_id = models.CharField(max_length=12, unique=True, editable=False)
    lab_order = models.ForeignKey(
        LabOrder,
        on_delete=models.CASCADE,
        related_name='results'
    )
    lab_test = models.ForeignKey(
        LabTest,
        on_delete=models.CASCADE,
        related_name='results'
    )

    # Result data
    numeric_value = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    text_value = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=RESULT_STATUS, default='PENDING')
    abnormal_flag = models.CharField(max_length=15, choices=ABNORMAL_FLAGS, default='NORMAL')

    # Reference ranges (can override test defaults)
    reference_range_min = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    reference_range_max = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    reference_range_text = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, blank=True)

    # Comments and notes
    technician_notes = models.TextField(blank=True)
    pathologist_notes = models.TextField(blank=True)

    # Staff and timestamps
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_lab_results'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_lab_results'
    )
    performed_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['lab_order']),
            models.Index(fields=['lab_test']),
            models.Index(fields=['status']),
            models.Index(fields=['abnormal_flag']),
        ]

    def __str__(self):
        return f"{self.result_id} - {self.lab_test.name}"

    def save(self, *args, **kwargs):
        if not self.result_id:
            self.result_id = f"RES{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def is_abnormal(self):
        """Check if result is abnormal."""
        return self.abnormal_flag != 'NORMAL'

    @property
    def is_critical(self):
        """Check if result is critical."""
        return self.abnormal_flag in ['CRITICAL_HIGH', 'CRITICAL_LOW']


class ImagingStudy(models.Model):
    """Medical imaging studies and reports."""

    STUDY_TYPES = [
        ('XRAY', 'X-Ray'),
        ('CT', 'CT Scan'),
        ('MRI', 'MRI'),
        ('ULTRASOUND', 'Ultrasound'),
        ('MAMMOGRAPHY', 'Mammography'),
        ('NUCLEAR', 'Nuclear Medicine'),
        ('PET', 'PET Scan'),
        ('FLUOROSCOPY', 'Fluoroscopy'),
        ('ANGIOGRAPHY', 'Angiography'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REPORTED', 'Reported'),
        ('CANCELLED', 'Cancelled'),
    ]

    study_id = models.CharField(max_length=12, unique=True, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='imaging_studies'
    )
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='imaging_studies'
    )
    ordering_doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='ordered_imaging_studies'
    )

    # Study details
    study_type = models.CharField(max_length=20, choices=STUDY_TYPES)
    body_part = models.CharField(max_length=100)
    clinical_indication = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED')

    # Scheduling
    scheduled_date = models.DateTimeField()
    performed_date = models.DateTimeField(null=True, blank=True)

    # Technical details
    contrast_used = models.BooleanField(default=False)
    contrast_type = models.CharField(max_length=100, blank=True)
    technique = models.TextField(blank=True)

    # Staff
    technologist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_imaging_studies'
    )
    radiologist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interpreted_imaging_studies'
    )

    # Report
    findings = models.TextField(blank=True)
    impression = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    report_date = models.DateTimeField(null=True, blank=True)

    # Files and images
    dicom_study_uid = models.CharField(max_length=100, blank=True)
    image_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['patient', '-scheduled_date']),
            models.Index(fields=['ordering_doctor', '-scheduled_date']),
            models.Index(fields=['study_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.study_id} - {self.study_type} ({self.body_part})"

    def save(self, *args, **kwargs):
        if not self.study_id:
            self.study_id = f"IMG{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class InsuranceProvider(models.Model):
    """Insurance provider information."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    # Contract details
    is_active = models.BooleanField(default=True)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PatientInsurance(models.Model):
    """Patient insurance coverage information."""

    COVERAGE_TYPES = [
        ('PRIMARY', 'Primary'),
        ('SECONDARY', 'Secondary'),
        ('TERTIARY', 'Tertiary'),
    ]

    RELATIONSHIP_CHOICES = [
        ('SELF', 'Self'),
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('PARENT', 'Parent'),
        ('OTHER', 'Other'),
    ]

    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='insurance_coverages'
    )
    insurance_provider = models.ForeignKey(
        InsuranceProvider,
        on_delete=models.CASCADE,
        related_name='patient_coverages'
    )

    # Coverage details
    coverage_type = models.CharField(max_length=10, choices=COVERAGE_TYPES, default='PRIMARY')
    policy_number = models.CharField(max_length=50)
    group_number = models.CharField(max_length=50, blank=True)
    member_id = models.CharField(max_length=50)

    # Policyholder information
    policyholder_name = models.CharField(max_length=200)
    relationship_to_patient = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES, default='SELF')
    policyholder_dob = models.DateField(null=True, blank=True)

    # Coverage dates
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)

    # Financial details
    copay_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    out_of_pocket_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['coverage_type', '-effective_date']
        unique_together = ['patient', 'coverage_type', 'insurance_provider']
        indexes = [
            models.Index(fields=['patient', 'coverage_type']),
            models.Index(fields=['policy_number']),
            models.Index(fields=['member_id']),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.insurance_provider.name} ({self.coverage_type})"

    @property
    def is_expired(self):
        """Check if insurance coverage has expired."""
        if self.expiration_date:
            return timezone.now().date() > self.expiration_date
        return False


class AuditLog(models.Model):
    """Comprehensive audit logging for medical records."""

    ACTION_TYPES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('VIEW', 'Viewed'),
        ('PRINT', 'Printed'),
        ('EXPORT', 'Exported'),
        ('SHARE', 'Shared'),
    ]

    # Record information
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()

    # Action details
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    description = models.TextField(blank=True)

    # User and session
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Additional data
    changes = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.user} {self.action} {self.content_type} at {self.timestamp}"
