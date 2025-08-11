"""
Premium HMS Analytics Models
Advanced business intelligence and reporting models
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class AnalyticsReport(models.Model):
    """Predefined analytics reports."""
    
    REPORT_TYPES = [
        ('FINANCIAL', 'Financial'),
        ('OPERATIONAL', 'Operational'),
        ('CLINICAL', 'Clinical'),
        ('PATIENT', 'Patient Analytics'),
        ('STAFF', 'Staff Performance'),
        ('QUALITY', 'Quality Metrics'),
        ('COMPLIANCE', 'Compliance'),
    ]
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
        ('ON_DEMAND', 'On Demand'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    frequency = models.CharField(max_length=15, choices=FREQUENCY_CHOICES, default='MONTHLY')
    
    # Report configuration
    sql_query = models.TextField(blank=True, help_text="SQL query for data extraction")
    parameters = models.JSONField(default=dict, blank=True)
    chart_config = models.JSONField(default=dict, blank=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_roles = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_reports'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['report_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"


class ReportExecution(models.Model):
    """Track report execution history."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    execution_id = models.CharField(max_length=12, unique=True, editable=False)
    report = models.ForeignKey(
        AnalyticsReport,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    # Execution details
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    parameters_used = models.JSONField(default=dict, blank=True)
    
    # Results
    result_data = models.JSONField(default=dict, blank=True)
    row_count = models.PositiveIntegerField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    
    # Performance metrics
    execution_time_seconds = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    memory_usage_mb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    
    # User and timestamps
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_executions'
    )
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['report', '-started_at']),
            models.Index(fields=['executed_by', '-started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.execution_id} - {self.report.name}"
    
    def save(self, *args, **kwargs):
        if not self.execution_id:
            self.execution_id = f"EX{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class KPIMetric(models.Model):
    """Key Performance Indicator definitions."""
    
    METRIC_TYPES = [
        ('COUNT', 'Count'),
        ('PERCENTAGE', 'Percentage'),
        ('AVERAGE', 'Average'),
        ('SUM', 'Sum'),
        ('RATIO', 'Ratio'),
        ('RATE', 'Rate'),
    ]
    
    CATEGORIES = [
        ('FINANCIAL', 'Financial'),
        ('OPERATIONAL', 'Operational'),
        ('CLINICAL', 'Clinical Quality'),
        ('PATIENT_SATISFACTION', 'Patient Satisfaction'),
        ('STAFF_PERFORMANCE', 'Staff Performance'),
        ('EFFICIENCY', 'Efficiency'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=25, choices=CATEGORIES)
    metric_type = models.CharField(max_length=15, choices=METRIC_TYPES)
    
    # Calculation
    calculation_method = models.TextField(help_text="Description of how this metric is calculated")
    sql_query = models.TextField(blank=True)
    
    # Target values
    target_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    warning_threshold = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    critical_threshold = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Display settings
    unit = models.CharField(max_length=20, blank=True)
    decimal_places = models.PositiveIntegerField(default=2)
    chart_type = models.CharField(max_length=20, default='line')
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_kpis'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'KPI Metric'
        verbose_name_plural = 'KPI Metrics'
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class KPIValue(models.Model):
    """Historical KPI values."""
    
    kpi_metric = models.ForeignKey(
        KPIMetric,
        on_delete=models.CASCADE,
        related_name='values'
    )
    
    # Value data
    value = models.DecimalField(max_digits=15, decimal_places=4)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Context
    context_data = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    calculated_at = models.DateTimeField(default=timezone.now)
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='calculated_kpi_values'
    )
    
    class Meta:
        ordering = ['-period_end']
        unique_together = ['kpi_metric', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['kpi_metric', '-period_end']),
            models.Index(fields=['-calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.kpi_metric.name}: {self.value} ({self.period_start.date()} - {self.period_end.date()})"
    
    @property
    def status(self):
        """Determine status based on thresholds."""
        kpi = self.kpi_metric
        
        if kpi.critical_threshold is not None:
            if self.value <= kpi.critical_threshold:
                return 'CRITICAL'
        
        if kpi.warning_threshold is not None:
            if self.value <= kpi.warning_threshold:
                return 'WARNING'
        
        if kpi.target_value is not None:
            if self.value >= kpi.target_value:
                return 'GOOD'
            else:
                return 'BELOW_TARGET'
        
        return 'NEUTRAL'


class Dashboard(models.Model):
    """Custom dashboards for different user roles."""
    
    DASHBOARD_TYPES = [
        ('EXECUTIVE', 'Executive Dashboard'),
        ('CLINICAL', 'Clinical Dashboard'),
        ('FINANCIAL', 'Financial Dashboard'),
        ('OPERATIONAL', 'Operational Dashboard'),
        ('DEPARTMENT', 'Department Dashboard'),
        ('PERSONAL', 'Personal Dashboard'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dashboard_type = models.CharField(max_length=15, choices=DASHBOARD_TYPES)
    
    # Configuration
    layout_config = models.JSONField(default=dict, blank=True)
    refresh_interval_minutes = models.PositiveIntegerField(default=15)
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_roles = models.JSONField(default=list, blank=True)
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='accessible_dashboards'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_dashboards'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['dashboard_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.dashboard_type})"


class DashboardWidget(models.Model):
    """Individual widgets within dashboards."""
    
    WIDGET_TYPES = [
        ('KPI_CARD', 'KPI Card'),
        ('CHART', 'Chart'),
        ('TABLE', 'Data Table'),
        ('GAUGE', 'Gauge'),
        ('PROGRESS', 'Progress Bar'),
        ('LIST', 'List'),
        ('CALENDAR', 'Calendar'),
        ('MAP', 'Map'),
    ]
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    
    # Widget configuration
    widget_type = models.CharField(max_length=15, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    
    # Data source
    kpi_metric = models.ForeignKey(
        KPIMetric,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='widgets'
    )
    report = models.ForeignKey(
        AnalyticsReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='widgets'
    )
    custom_query = models.TextField(blank=True)
    
    # Layout
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=4)
    height = models.PositiveIntegerField(default=3)
    
    # Display configuration
    chart_config = models.JSONField(default=dict, blank=True)
    display_options = models.JSONField(default=dict, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['dashboard', 'position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class UserAnalytics(models.Model):
    """Track user behavior and system usage analytics."""
    
    ACTION_TYPES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PAGE_VIEW', 'Page View'),
        ('SEARCH', 'Search'),
        ('EXPORT', 'Export'),
        ('PRINT', 'Print'),
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete Record'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_events'
    )
    
    # Event details
    action = models.CharField(max_length=15, choices=ACTION_TYPES)
    page_url = models.URLField(blank=True)
    page_title = models.CharField(max_length=200, blank=True)
    
    # Context data
    metadata = models.JSONField(default=dict, blank=True)
    session_id = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Performance metrics
    page_load_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.action} at {self.timestamp}"
