from rest_framework import permissions


class IsParent(permissions.BasePermission):
    """Only allow parents to access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'parent'


class IsSchoolAdmin(permissions.BasePermission):
    """Only allow school admins to access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsSuperAdmin(permissions.BasePermission):
    """Only allow super admins to access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'superadmin'


class IsTeacher(permissions.BasePermission):
    """Only allow teachers to access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'teacher'


class IsBursar(permissions.BasePermission):
    """Only allow bursars to access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'bursar'


class IsRoleOwnerOrAdmin(permissions.BasePermission):
    """
    Users can access their own role settings.
    Super Admin can access all.
    School Admin can edit their school settings.
    Object-level permission enforced.
    """
    def has_object_permission(self, request, view, obj):
        # Super Admin can access all
        if request.user.role == 'superadmin':
            return True
        
        # School Admin can access objects in their school
        if hasattr(obj, 'school') and request.user.role == 'admin':
            return obj.school == request.user.school
        
        # Teacher can access their own objects
        if hasattr(obj, 'teacher') and request.user.role == 'teacher':
            return obj.teacher == request.user
        
        # Parent can access their linked children
        if hasattr(obj, 'parents') and request.user.role == 'parent':
            return request.user in obj.parents.all()
        
        # Users can access their own profile
        return obj == request.user
