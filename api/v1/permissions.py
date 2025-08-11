"""
Premium HMS API Permissions
Advanced permission classes for role-based access control
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsPatientOwnerOrDoctor(permissions.BasePermission):
    """
    Permission for patient data - patients can access their own data,
    doctors can access their patients' data.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin has full access
        if user.role == 'ADMIN':
            return True
        
        # Patient can access their own data
        if user.role == 'PATIENT':
            return obj.user == user
        
        # Doctor can access their patients' data
        if user.role == 'DOCTOR':
            # Check if this patient has appointments with this doctor
            return obj.appointments.filter(doctor__user=user).exists()
        
        return False


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Permission that allows only doctors and admins.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['DOCTOR', 'ADMIN']
        )


class IsAppointmentParticipant(permissions.BasePermission):
    """
    Permission for appointments - only the patient, doctor, or admin can access.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin has full access
        if user.role == 'ADMIN':
            return True
        
        # Patient can access their own appointments
        if user.role == 'PATIENT':
            return obj.patient.user == user
        
        # Doctor can access their appointments
        if user.role == 'DOCTOR':
            return obj.doctor.user == user
        
        return False


class IsBillOwnerOrAdmin(permissions.BasePermission):
    """
    Permission for bills - only the patient or admin can access.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin has full access
        if user.role == 'ADMIN':
            return True
        
        # Patient can access their own bills
        if user.role == 'PATIENT':
            return obj.patient.user == user
        
        return False
