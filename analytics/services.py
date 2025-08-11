"""
Premium HMS Analytics Services
Advanced business intelligence and data analysis services
"""

from django.db import connection
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from patients.models import PatientProfile
from doctors.models import DoctorProfile
from appointments.models import Appointment
from billing.models import Bill, Payment
from .models import KPIMetric, KPIValue, AnalyticsReport, ReportExecution


class AnalyticsService:
    """Core analytics service for business intelligence."""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def get_dashboard_stats(self, date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics."""
        if not date_range:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            date_range = (start_date, end_date)
        
        start_date, end_date = date_range
        
        # Patient statistics
        total_patients = PatientProfile.objects.count()
        new_patients = PatientProfile.objects.filter(
            created_at__date__range=date_range
        ).count()
        
        # Doctor statistics
        total_doctors = DoctorProfile.objects.filter(is_available=True).count()
        
        # Appointment statistics
        total_appointments = Appointment.objects.filter(
            appointment_date__range=date_range
        ).count()
        
        today_appointments = Appointment.objects.filter(
            appointment_date=timezone.now().date()
        ).count()
        
        upcoming_appointments = Appointment.objects.filter(
            appointment_date__gt=timezone.now().date(),
            status__in=['PENDING', 'CONFIRMED']
        ).count()
        
        # Financial statistics
        revenue_data = Bill.objects.filter(
            created_at__date__range=date_range,
            status='PAID'
        ).aggregate(
            total_revenue=Sum('total_amount'),
            total_bills=Count('id')
        )
        
        monthly_revenue = revenue_data['total_revenue'] or 0
        
        # Department performance
        department_stats = self.get_department_performance(date_range)
        
        # Appointment trends
        appointment_trends = self.get_appointment_trends(date_range)
        
        return {
            'total_patients': total_patients,
            'new_patients': new_patients,
            'total_doctors': total_doctors,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'upcoming_appointments': upcoming_appointments,
            'monthly_revenue': float(monthly_revenue),
            'department_stats': department_stats,
            'appointment_trends': appointment_trends,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def get_department_performance(self, date_range: tuple) -> List[Dict[str, Any]]:
        """Get performance metrics by department."""
        start_date, end_date = date_range
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d.name as department_name,
                    COUNT(DISTINCT dp.id) as doctor_count,
                    COUNT(a.id) as appointment_count,
                    COALESCE(SUM(b.total_amount), 0) as revenue,
                    AVG(CASE WHEN a.status = 'COMPLETED' THEN 1 ELSE 0 END) * 100 as completion_rate
                FROM doctors_department d
                LEFT JOIN doctors_doctorprofile dp ON d.id = dp.department_id AND dp.is_available = true
                LEFT JOIN appointments_appointment a ON dp.id = a.doctor_id 
                    AND a.appointment_date BETWEEN %s AND %s
                LEFT JOIN billing_bill b ON a.id = b.appointment_id AND b.status = 'PAID'
                GROUP BY d.id, d.name
                ORDER BY revenue DESC
            """, [start_date, end_date])
            
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return results
    
    def get_appointment_trends(self, date_range: tuple) -> Dict[str, List]:
        """Get appointment trends over time."""
        start_date, end_date = date_range
        
        # Generate date range
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        # Get appointment counts by date
        appointment_counts = {}
        appointments = Appointment.objects.filter(
            appointment_date__range=date_range
        ).values('appointment_date').annotate(count=Count('id'))
        
        for item in appointments:
            appointment_counts[item['appointment_date']] = item['count']
        
        # Build trend data
        labels = []
        data = []
        
        for date in date_list:
            labels.append(date.strftime('%Y-%m-%d'))
            data.append(appointment_counts.get(date, 0))
        
        return {
            'labels': labels,
            'data': data
        }
    
    def get_financial_analytics(self, date_range: tuple) -> Dict[str, Any]:
        """Get comprehensive financial analytics."""
        start_date, end_date = date_range
        
        # Revenue analysis
        revenue_by_month = Bill.objects.filter(
            created_at__date__range=date_range,
            status='PAID'
        ).extra(
            select={'month': "DATE_TRUNC('month', created_at)"}
        ).values('month').annotate(
            revenue=Sum('total_amount'),
            bill_count=Count('id')
        ).order_by('month')
        
        # Payment method analysis
        payment_methods = Payment.objects.filter(
            payment_date__range=date_range
        ).values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Outstanding bills
        outstanding_bills = Bill.objects.filter(
            status__in=['SENT', 'DRAFT']
        ).aggregate(
            total_outstanding=Sum('total_amount'),
            count=Count('id')
        )
        
        # Average bill amount
        avg_bill_amount = Bill.objects.filter(
            created_at__date__range=date_range
        ).aggregate(avg_amount=Avg('total_amount'))
        
        return {
            'revenue_by_month': list(revenue_by_month),
            'payment_methods': list(payment_methods),
            'outstanding_bills': outstanding_bills,
            'avg_bill_amount': float(avg_bill_amount['avg_amount'] or 0)
        }
    
    def get_patient_analytics(self, date_range: tuple) -> Dict[str, Any]:
        """Get patient-related analytics."""
        start_date, end_date = date_range
        
        # Age distribution
        age_distribution = self.calculate_age_distribution()
        
        # Gender distribution
        gender_distribution = PatientProfile.objects.values(
            'user__gender'
        ).annotate(count=Count('id'))
        
        # New patient trends
        new_patients_by_month = PatientProfile.objects.filter(
            created_at__date__range=date_range
        ).extra(
            select={'month': "DATE_TRUNC('month', created_at)"}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Patient retention (patients with multiple visits)
        repeat_patients = PatientProfile.objects.annotate(
            visit_count=Count('appointments')
        ).filter(visit_count__gt=1).count()
        
        total_patients = PatientProfile.objects.count()
        retention_rate = (repeat_patients / total_patients * 100) if total_patients > 0 else 0
        
        return {
            'age_distribution': age_distribution,
            'gender_distribution': list(gender_distribution),
            'new_patients_by_month': list(new_patients_by_month),
            'retention_rate': round(retention_rate, 2),
            'repeat_patients': repeat_patients,
            'total_patients': total_patients
        }
    
    def calculate_age_distribution(self) -> Dict[str, int]:
        """Calculate patient age distribution."""
        age_ranges = {
            '0-18': 0, '19-30': 0, '31-50': 0, '51-70': 0, '70+': 0
        }
        
        patients = PatientProfile.objects.select_related('user').all()
        
        for patient in patients:
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
    
    def calculate_kpi_values(self, kpi_metric: KPIMetric, period_start: datetime, period_end: datetime) -> float:
        """Calculate KPI values based on metric definition."""
        
        if kpi_metric.sql_query:
            # Execute custom SQL query
            with connection.cursor() as cursor:
                cursor.execute(kpi_metric.sql_query, [period_start, period_end])
                result = cursor.fetchone()
                return float(result[0]) if result and result[0] is not None else 0.0
        
        # Default calculations based on metric name
        metric_name = kpi_metric.name.lower()
        
        if 'patient satisfaction' in metric_name:
            # Mock calculation - in real system, this would come from surveys
            return 4.2  # out of 5
        
        elif 'appointment completion rate' in metric_name:
            total_appointments = Appointment.objects.filter(
                appointment_date__range=[period_start.date(), period_end.date()]
            ).count()
            
            completed_appointments = Appointment.objects.filter(
                appointment_date__range=[period_start.date(), period_end.date()],
                status='COMPLETED'
            ).count()
            
            return (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
        
        elif 'average wait time' in metric_name:
            # Mock calculation - in real system, this would track actual wait times
            return 15.5  # minutes
        
        elif 'revenue per patient' in metric_name:
            total_revenue = Bill.objects.filter(
                created_at__range=[period_start, period_end],
                status='PAID'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            unique_patients = Bill.objects.filter(
                created_at__range=[period_start, period_end],
                status='PAID'
            ).values('patient').distinct().count()
            
            return float(total_revenue / unique_patients) if unique_patients > 0 else 0
        
        return 0.0
    
    def generate_report(self, report: AnalyticsReport, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate analytics report."""
        execution = ReportExecution.objects.create(
            report=report,
            executed_by=parameters.get('user') if parameters else None,
            parameters_used=parameters or {}
        )
        
        try:
            execution.status = 'RUNNING'
            execution.save()
            
            start_time = timezone.now()
            
            if report.sql_query:
                # Execute custom SQL query
                with connection.cursor() as cursor:
                    cursor.execute(report.sql_query)
                    columns = [col[0] for col in cursor.description]
                    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                # Generate default report based on type
                data = self.generate_default_report(report.report_type, parameters)
            
            end_time = timezone.now()
            execution_time = (end_time - start_time).total_seconds()
            
            execution.status = 'COMPLETED'
            execution.result_data = {'data': data}
            execution.row_count = len(data) if isinstance(data, list) else 1
            execution.execution_time_seconds = execution_time
            execution.completed_at = end_time
            execution.save()
            
            return {
                'execution_id': execution.execution_id,
                'status': 'COMPLETED',
                'data': data,
                'row_count': execution.row_count,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution.status = 'FAILED'
            execution.error_message = str(e)
            execution.save()
            
            return {
                'execution_id': execution.execution_id,
                'status': 'FAILED',
                'error': str(e)
            }
    
    def generate_default_report(self, report_type: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate default reports based on type."""
        
        if report_type == 'FINANCIAL':
            return self.generate_financial_report(parameters)
        elif report_type == 'OPERATIONAL':
            return self.generate_operational_report(parameters)
        elif report_type == 'CLINICAL':
            return self.generate_clinical_report(parameters)
        elif report_type == 'PATIENT':
            return self.generate_patient_report(parameters)
        else:
            return []
    
    def generate_financial_report(self, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate financial performance report."""
        # Implementation would include detailed financial analysis
        return [
            {
                'metric': 'Total Revenue',
                'value': 125000.00,
                'period': 'Current Month',
                'change': '+12%'
            },
            {
                'metric': 'Outstanding Bills',
                'value': 15000.00,
                'period': 'Current',
                'change': '-5%'
            }
        ]
    
    def generate_operational_report(self, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate operational efficiency report."""
        return [
            {
                'metric': 'Appointment Utilization',
                'value': '85%',
                'target': '90%',
                'status': 'Below Target'
            },
            {
                'metric': 'Average Wait Time',
                'value': '15 minutes',
                'target': '10 minutes',
                'status': 'Above Target'
            }
        ]
    
    def generate_clinical_report(self, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate clinical quality report."""
        return [
            {
                'metric': 'Patient Satisfaction',
                'value': '4.2/5',
                'target': '4.5/5',
                'status': 'Below Target'
            },
            {
                'metric': 'Readmission Rate',
                'value': '3.2%',
                'target': '<5%',
                'status': 'Good'
            }
        ]
    
    def generate_patient_report(self, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate patient analytics report."""
        return [
            {
                'metric': 'New Patients',
                'value': 45,
                'period': 'This Month',
                'change': '+8%'
            },
            {
                'metric': 'Patient Retention',
                'value': '78%',
                'target': '80%',
                'status': 'Close to Target'
            }
        ]
