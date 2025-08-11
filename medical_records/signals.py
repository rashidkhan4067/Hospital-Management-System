"""
Premium HMS Medical Records Signals
Automatic audit logging and data integrity enforcement
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils import timezone
import threading

from .models import (
    MedicalRecord, Prescription, LabOrder, LabResult, 
    ImagingStudy, PatientInsurance, AuditLog
)

User = get_user_model()

# Thread-local storage for request data
_thread_locals = threading.local()


def get_current_request():
    """Get the current request from thread-local storage."""
    return getattr(_thread_locals, 'request', None)


def set_current_request(request):
    """Set the current request in thread-local storage."""
    _thread_locals.request = request


class AuditLogMiddleware:
    """Middleware to capture request information for audit logging."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        set_current_request(request)
        response = self.get_response(request)
        set_current_request(None)
        return response


def create_audit_log(instance, action, user=None, changes=None, description=''):
    """Create an audit log entry."""
    request = get_current_request()
    
    if not user and request:
        user = getattr(request, 'user', None)
        if user and user.is_anonymous:
            user = None
    
    ip_address = None
    user_agent = ''
    session_key = ''
    
    if request:
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get session key
        session_key = request.session.session_key or ''
    
    AuditLog.objects.create(
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        action=action,
        description=description,
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent,
        changes=changes or {},
        metadata={
            'model_name': instance.__class__.__name__,
            'timestamp': timezone.now().isoformat(),
        }
    )


@receiver(post_save, sender=MedicalRecord)
def log_medical_record_save(sender, instance, created, **kwargs):
    """Log medical record creation and updates."""
    action = 'CREATE' if created else 'UPDATE'
    description = f"Medical record {action.lower()}d for patient {instance.patient.full_name}"
    
    changes = {}
    if not created and hasattr(instance, '_old_values'):
        # Track changes if we have old values
        for field in ['chief_complaint', 'assessment', 'plan', 'priority']:
            old_value = instance._old_values.get(field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changes[field] = {'old': old_value, 'new': new_value}
    
    create_audit_log(instance, action, changes=changes, description=description)


@receiver(pre_save, sender=MedicalRecord)
def store_medical_record_old_values(sender, instance, **kwargs):
    """Store old values before saving for change tracking."""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_values = {
                'chief_complaint': old_instance.chief_complaint,
                'assessment': old_instance.assessment,
                'plan': old_instance.plan,
                'priority': old_instance.priority,
            }
        except sender.DoesNotExist:
            instance._old_values = {}
    else:
        instance._old_values = {}


@receiver(post_save, sender=Prescription)
def log_prescription_save(sender, instance, created, **kwargs):
    """Log prescription creation and updates."""
    action = 'CREATE' if created else 'UPDATE'
    description = f"Prescription {action.lower()}d for patient {instance.patient.full_name}"
    create_audit_log(instance, action, description=description)


@receiver(post_save, sender=LabOrder)
def log_lab_order_save(sender, instance, created, **kwargs):
    """Log lab order creation and updates."""
    action = 'CREATE' if created else 'UPDATE'
    description = f"Lab order {action.lower()}d for patient {instance.patient.full_name}"
    
    changes = {}
    if not created and hasattr(instance, '_old_status'):
        if instance._old_status != instance.status:
            changes['status'] = {'old': instance._old_status, 'new': instance.status}
    
    create_audit_log(instance, action, changes=changes, description=description)


@receiver(pre_save, sender=LabOrder)
def store_lab_order_old_status(sender, instance, **kwargs):
    """Store old status before saving for change tracking."""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=LabResult)
def log_lab_result_save(sender, instance, created, **kwargs):
    """Log lab result creation and updates."""
    action = 'CREATE' if created else 'UPDATE'
    description = f"Lab result {action.lower()}d for test {instance.lab_test.name}"
    
    changes = {}
    if not created and hasattr(instance, '_old_values'):
        for field in ['numeric_value', 'text_value', 'status', 'abnormal_flag']:
            old_value = instance._old_values.get(field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changes[field] = {'old': str(old_value), 'new': str(new_value)}
    
    create_audit_log(instance, action, changes=changes, description=description)


@receiver(pre_save, sender=LabResult)
def store_lab_result_old_values(sender, instance, **kwargs):
    """Store old values before saving for change tracking."""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_values = {
                'numeric_value': old_instance.numeric_value,
                'text_value': old_instance.text_value,
                'status': old_instance.status,
                'abnormal_flag': old_instance.abnormal_flag,
            }
        except sender.DoesNotExist:
            instance._old_values = {}
    else:
        instance._old_values = {}


@receiver(post_save, sender=ImagingStudy)
def log_imaging_study_save(sender, instance, created, **kwargs):
    """Log imaging study creation and updates."""
    action = 'CREATE' if created else 'UPDATE'
    description = f"Imaging study {action.lower()}d: {instance.study_type} for patient {instance.patient.full_name}"
    create_audit_log(instance, action, description=description)


@receiver(post_save, sender=PatientInsurance)
def log_patient_insurance_save(sender, instance, created, **kwargs):
    """Log patient insurance creation and updates."""
    action = 'CREATE' if created else 'UPDATE'
    description = f"Insurance coverage {action.lower()}d for patient {instance.patient.full_name}"
    create_audit_log(instance, action, description=description)


@receiver(post_delete)
def log_model_deletion(sender, instance, **kwargs):
    """Log deletion of tracked models."""
    tracked_models = [
        MedicalRecord, Prescription, LabOrder, LabResult, 
        ImagingStudy, PatientInsurance
    ]
    
    if sender in tracked_models:
        description = f"{sender.__name__} deleted"
        if hasattr(instance, 'patient'):
            description += f" for patient {instance.patient.full_name}"
        
        create_audit_log(instance, 'DELETE', description=description)


# Data integrity signals
@receiver(post_save, sender=LabResult)
def check_critical_lab_results(sender, instance, created, **kwargs):
    """Check for critical lab results and trigger notifications."""
    if instance.is_critical and instance.status == 'FINAL':
        # Import here to avoid circular imports
        from notifications.models import Notification, NotificationType
        
        try:
            critical_result_type = NotificationType.objects.get(name='Critical Lab Result')
            
            # Notify the ordering doctor
            Notification.objects.create(
                notification_type=critical_result_type,
                recipient=instance.lab_order.doctor.user,
                title='Critical Lab Result',
                message=f'Critical result for {instance.lab_test.name}: {instance.numeric_value or instance.text_value}',
                channel='IN_APP',
                data={
                    'lab_result_id': instance.result_id,
                    'patient_id': instance.lab_order.patient.patient_id,
                    'test_name': instance.lab_test.name,
                    'value': str(instance.numeric_value or instance.text_value),
                    'abnormal_flag': instance.abnormal_flag,
                }
            )
        except NotificationType.DoesNotExist:
            pass  # Notification type not configured


@receiver(post_save, sender=Prescription)
def check_drug_interactions(sender, instance, created, **kwargs):
    """Check for potential drug interactions."""
    if created:
        # Get all active prescriptions for the patient
        active_prescriptions = Prescription.objects.filter(
            patient=instance.patient,
            status='ACTIVE'
        ).exclude(pk=instance.pk)
        
        # Get all medications in active prescriptions
        current_medications = []
        for prescription in active_prescriptions:
            current_medications.extend(
                prescription.medications.values_list('medication__name', flat=True)
            )
        
        # Get medications in the new prescription
        new_medications = instance.medications.values_list('medication__name', flat=True)
        
        # Simple interaction check (in a real system, this would use a drug interaction database)
        potential_interactions = []
        for new_med in new_medications:
            for current_med in current_medications:
                if new_med.lower() in ['warfarin', 'aspirin'] and current_med.lower() in ['warfarin', 'aspirin']:
                    potential_interactions.append(f"{new_med} + {current_med}")
        
        if potential_interactions:
            # Create audit log for potential interaction
            create_audit_log(
                instance, 
                'UPDATE',
                description=f"Potential drug interactions detected: {', '.join(potential_interactions)}",
                changes={'interactions': potential_interactions}
            )
