"""
Premium HMS API v1 Views
Ultra-modern ViewSets with advanced features, filtering, and permissions
"""

from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from patients.models import PatientProfile, MedicalRecord
from doctors.models import DoctorProfile, Department, Schedule
from appointments.models import Appointment
from billing.models import Bill, BillItem, Payment

from .serializers import (
    PatientProfileSerializer,
    DoctorProfileSerializer,
    AppointmentSerializer,
    BillSerializer,
    DepartmentSerializer,
    MedicalRecordSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List all patients",
        description="Retrieve a paginated list of all patients with filtering and search capabilities"
    ),
    create=extend_schema(
        summary="Create new patient",
        description="Create a new patient profile with user account"
    ),
    retrieve=extend_schema(
        summary="Get patient details",
        description="Retrieve detailed information about a specific patient"
    ),
    update=extend_schema(
        summary="Update patient",
        description="Update patient profile information"
    ),
    destroy=extend_schema(
        summary="Delete patient",
        description="Delete a patient profile (admin only)"
    ),
)
class PatientViewSet(viewsets.ModelViewSet):
    """
    Ultra-modern Patient Management ViewSet
    
    Provides comprehensive CRUD operations for patient management with
    advanced filtering, search, and analytics capabilities.
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['blood_group', 'user__role']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'patient_id']
    ordering_fields = ['created_at', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset with optimized queries and user-based filtering."""
        queryset = PatientProfile.objects.select_related('user').prefetch_related('medical_records', 'appointments')
        
        # Filter based on user role
        if self.request.user.role == 'PATIENT':
            queryset = queryset.filter(user=self.request.user)
        elif self.request.user.role == 'DOCTOR':
            # Doctors can see their patients
            queryset = queryset.filter(appointments__doctor__user=self.request.user).distinct()
        
        return queryset
    
    @extend_schema(
        summary="Get patient statistics",
        description="Retrieve comprehensive statistics for patients",
        responses={200: "Patient statistics"}
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get comprehensive patient statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_patients': queryset.count(),
            'blood_group_distribution': dict(
                queryset.values('blood_group').annotate(count=Count('id')).values_list('blood_group', 'count')
            ),
            'age_distribution': self._get_age_distribution(queryset),
            'recent_registrations': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
            'patients_with_appointments': queryset.filter(appointments__isnull=False).distinct().count(),
        }
        
        return Response(stats)
    
    @extend_schema(
        summary="Get patient medical history",
        description="Retrieve complete medical history for a patient",
        responses={200: "Medical history"}
    )
    @action(detail=True, methods=['get'])
    def medical_history(self, request, pk=None):
        """Get complete medical history for a patient."""
        patient = self.get_object()
        medical_records = patient.medical_records.select_related('doctor__user').order_by('-visit_date')
        
        serializer = MedicalRecordSerializer(medical_records, many=True)
        return Response({
            'patient': PatientProfileSerializer(patient).data,
            'medical_records': serializer.data,
            'total_visits': medical_records.count(),
        })
    
    def _get_age_distribution(self, queryset):
        """Calculate age distribution of patients."""
        age_ranges = {
            '0-18': 0, '19-30': 0, '31-50': 0, '51-70': 0, '70+': 0
        }
        
        for patient in queryset:
            age = patient.age
            if age is not None:
                if age <= 18:
                    age_ranges['0-18'] += 1
                elif age <= 30:
                    age_ranges['19-30'] += 1
                elif age <= 50:
                    age_ranges['31-50'] += 1
                elif age <= 70:
                    age_ranges['51-70'] += 1
                else:
                    age_ranges['70+'] += 1
        
        return age_ranges


@extend_schema_view(
    list=extend_schema(
        summary="List all doctors",
        description="Retrieve a paginated list of all doctors with filtering capabilities"
    ),
    create=extend_schema(
        summary="Create new doctor",
        description="Create a new doctor profile with user account"
    ),
)
class DoctorViewSet(viewsets.ModelViewSet):
    """
    Advanced Doctor Management ViewSet
    
    Comprehensive doctor management with specialization filtering,
    availability tracking, and performance analytics.
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'department', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'doctor_id', 'qualification']
    ordering_fields = ['created_at', 'user__first_name', 'experience_years', 'consultation_fee']
    ordering = ['user__first_name']
    
    def get_queryset(self):
        """Get optimized queryset with related data."""
        return DoctorProfile.objects.select_related('user', 'department').prefetch_related('schedules', 'appointments')
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get list of available doctors."""
        available_doctors = self.get_queryset().filter(is_available=True)
        serializer = self.get_serializer(available_doctors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Get doctor's schedule."""
        doctor = self.get_object()
        schedules = doctor.schedules.filter(is_active=True).order_by('day_of_week')
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'day': schedule.get_day_of_week_display(),
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
                'max_appointments': schedule.max_appointments,
            })
        
        return Response({
            'doctor': self.get_serializer(doctor).data,
            'schedule': schedule_data,
        })


@extend_schema_view(
    list=extend_schema(
        summary="List appointments",
        description="Retrieve appointments with advanced filtering and search"
    ),
)
class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Intelligent Appointment Management ViewSet
    
    Advanced appointment scheduling with conflict detection,
    automated reminders, and comprehensive analytics.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'doctor', 'patient']
    search_fields = ['appointment_id', 'patient__user__first_name', 'doctor__user__first_name']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['-appointment_date', '-appointment_time']
    
    def get_queryset(self):
        """Get queryset with user-based filtering."""
        queryset = Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__department')
        
        if self.request.user.role == 'PATIENT':
            queryset = queryset.filter(patient__user=self.request.user)
        elif self.request.user.role == 'DOCTOR':
            queryset = queryset.filter(doctor__user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments."""
        upcoming = self.get_queryset().filter(
            appointment_date__gte=timezone.now().date(),
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('appointment_date', 'appointment_time')
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments."""
        today = timezone.now().date()
        today_appointments = self.get_queryset().filter(appointment_date=today)
        
        serializer = self.get_serializer(today_appointments, many=True)
        return Response({
            'date': today,
            'appointments': serializer.data,
            'total': today_appointments.count(),
        })


class DepartmentViewSet(viewsets.ModelViewSet):
    """Department Management ViewSet."""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """Medical Records Management ViewSet."""
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    def get_queryset(self):
        """Get medical records based on user role."""
        queryset = MedicalRecord.objects.select_related('patient__user', 'doctor__user')
        
        if self.request.user.role == 'PATIENT':
            queryset = queryset.filter(patient__user=self.request.user)
        elif self.request.user.role == 'DOCTOR':
            queryset = queryset.filter(doctor__user=self.request.user)
        
        return queryset


class BillViewSet(viewsets.ModelViewSet):
    """
    Advanced Billing Management ViewSet
    
    Comprehensive billing system with payment tracking,
    automated calculations, and financial analytics.
    """
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'patient']
    search_fields = ['bill_number', 'patient__user__first_name', 'patient__user__last_name']
    ordering_fields = ['created_at', 'due_date', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get bills with user-based filtering."""
        queryset = Bill.objects.select_related('patient__user', 'appointment').prefetch_related('items', 'payments')
        
        if self.request.user.role == 'PATIENT':
            queryset = queryset.filter(patient__user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue bills."""
        overdue_bills = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status__in=['SENT', 'DRAFT']
        )
        
        serializer = self.get_serializer(overdue_bills, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get billing summary statistics."""
        queryset = self.get_queryset()
        
        summary = {
            'total_bills': queryset.count(),
            'total_amount': queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'paid_amount': queryset.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0,
            'pending_amount': queryset.filter(status__in=['SENT', 'DRAFT']).aggregate(
                Sum('total_amount'))['total_amount__sum'] or 0,
            'overdue_count': queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['SENT', 'DRAFT']
            ).count(),
        }
        
        summary['outstanding_amount'] = summary['total_amount'] - summary['paid_amount']
        
        return Response(summary)
