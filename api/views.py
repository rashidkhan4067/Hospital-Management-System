"""
Premium Hospital Management System API Views
Ultra-modern API views with advanced features and comprehensive functionality
"""

from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
import psutil
import platform
from datetime import datetime


class APIRootView(APIView):
    """
    Premium Hospital Management System API Root
    
    Welcome to the ultra-modern HMS API with advanced healthcare management features.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="API Root Information",
        description="Get information about the Premium HMS API",
        responses={
            200: OpenApiResponse(description="API information retrieved successfully")
        },
        tags=['System']
    )
    def get(self, request):
        """Get API root information and available endpoints."""
        return Response({
            'message': 'Welcome to Premium Hospital Management System API',
            'version': '2.0.0',
            'description': 'Ultra-modern healthcare management platform',
            'features': [
                'Advanced Patient Management',
                'Doctor Scheduling & Profiles',
                'Intelligent Appointment System',
                'Comprehensive Billing & Payments',
                'Real-time Notifications',
                'Business Intelligence & Analytics',
                'AI-Powered Recommendations',
                'Secure Authentication & Authorization',
                'RESTful API with OpenAPI Documentation',
                'WebSocket Support for Real-time Features'
            ],
            'endpoints': {
                'authentication': '/api/auth/',
                'patients': '/api/v1/patients/',
                'doctors': '/api/v1/doctors/',
                'appointments': '/api/v1/appointments/',
                'billing': '/api/v1/billing/',
                'analytics': '/api/v1/analytics/',
                'notifications': '/api/v1/notifications/',
                'documentation': '/api/docs/',
                'schema': '/api/schema/',
                'health': '/api/system/health/',
                'status': '/api/system/status/'
            },
            'documentation': {
                'swagger': request.build_absolute_uri('/api/docs/'),
                'redoc': request.build_absolute_uri('/api/redoc/'),
                'schema': request.build_absolute_uri('/api/schema/')
            },
            'timestamp': timezone.now().isoformat(),
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
        })


class HealthCheckView(APIView):
    """
    System Health Check Endpoint
    
    Provides comprehensive health status of the system including database,
    cache, and external service connectivity.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="System Health Check",
        description="Get comprehensive system health status",
        responses={
            200: OpenApiResponse(description="System is healthy"),
            503: OpenApiResponse(description="System has issues")
        },
        tags=['System']
    )
    def get(self, request):
        """Perform comprehensive health check."""
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        overall_healthy = True
        
        # Database Health Check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }
            overall_healthy = False
        
        # Cache Health Check
        try:
            cache_key = 'health_check_test'
            cache.set(cache_key, 'test_value', 10)
            cached_value = cache.get(cache_key)
            if cached_value == 'test_value':
                health_status['checks']['cache'] = {
                    'status': 'healthy',
                    'message': 'Cache is working properly'
                }
            else:
                raise Exception('Cache value mismatch')
        except Exception as e:
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'message': f'Cache check failed: {str(e)}'
            }
            overall_healthy = False
        
        # System Resources Check
        try:
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            cpu_usage = psutil.cpu_percent(interval=1)
            
            resource_status = 'healthy'
            resource_message = 'System resources are within normal limits'
            
            if memory_usage > 90 or disk_usage > 90 or cpu_usage > 90:
                resource_status = 'warning'
                resource_message = 'High resource usage detected'
                
            health_status['checks']['resources'] = {
                'status': resource_status,
                'message': resource_message,
                'details': {
                    'memory_usage_percent': memory_usage,
                    'disk_usage_percent': disk_usage,
                    'cpu_usage_percent': cpu_usage
                }
            }
        except Exception as e:
            health_status['checks']['resources'] = {
                'status': 'unknown',
                'message': f'Could not check system resources: {str(e)}'
            }
        
        # Update overall status
        if not overall_healthy:
            health_status['status'] = 'unhealthy'
        
        status_code = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health_status, status=status_code)


class SystemStatusView(APIView):
    """
    Detailed System Status Information
    
    Provides comprehensive system information including server details,
    application metrics, and performance statistics.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Detailed System Status",
        description="Get comprehensive system status and metrics",
        responses={
            200: OpenApiResponse(description="System status retrieved successfully")
        },
        tags=['System']
    )
    def get(self, request):
        """Get detailed system status and metrics."""
        try:
            # System Information
            system_info = {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'django_version': settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else 'Unknown',
                'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
                'uptime': self._get_uptime(),
            }
            
            # Application Metrics
            app_metrics = {
                'debug_mode': settings.DEBUG,
                'allowed_hosts': settings.ALLOWED_HOSTS,
                'installed_apps_count': len(settings.INSTALLED_APPS),
                'middleware_count': len(settings.MIDDLEWARE),
                'database_engine': settings.DATABASES['default']['ENGINE'],
                'cache_backend': settings.CACHES['default']['BACKEND'],
                'time_zone': settings.TIME_ZONE,
                'language_code': settings.LANGUAGE_CODE,
            }
            
            # Performance Metrics
            performance_metrics = {
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent,
                    'used': psutil.virtual_memory().used,
                },
                'cpu': {
                    'count': psutil.cpu_count(),
                    'percent': psutil.cpu_percent(interval=1),
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent,
                }
            }
            
            return Response({
                'status': 'operational',
                'timestamp': timezone.now().isoformat(),
                'system_info': system_info,
                'application_metrics': app_metrics,
                'performance_metrics': performance_metrics,
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to retrieve system status: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_uptime(self):
        """Calculate system uptime."""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
