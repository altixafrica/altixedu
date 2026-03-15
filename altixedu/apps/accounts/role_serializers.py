"""
Serializers for Custom Roles and Advanced Permission System
"""

from rest_framework import serializers
from apps.accounts.role_models import (
    CustomRole,
    RoleUserAssignment,
    StudentClassroomAssignment,
    ParentStudentLink
)
from apps.accounts.models import User
from apps.students.models import Student


class CustomRoleSerializer(serializers.ModelSerializer):
    """Serializer for custom roles"""
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    school_name = serializers.CharField(
        source='school.name',
        read_only=True
    )
    
    class Meta:
        model = CustomRole
        fields = [
            'id', 'school', 'school_name', 'name', 'description',
            'based_on', 'permissions', 'dashboard_template', 'visible_modules',
            'can_manage_users', 'can_manage_finances', 'can_manage_academics',
            'can_view_reports', 'can_export_data', 'is_active',
            'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RoleUserAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for assigning custom roles to users"""
    user_full_name = serializers.CharField(
        source='user.get_full_name',
        read_only=True
    )
    role_name = serializers.CharField(
        source='role.name',
        read_only=True
    )
    assigned_by_name = serializers.CharField(
        source='assigned_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = RoleUserAssignment
        fields = [
            'id', 'user', 'user_full_name', 'role', 'role_name',
            'is_active', 'assigned_at', 'assigned_by', 'assigned_by_name',
            'expires_at'
        ]
        read_only_fields = ['assigned_at']


class StudentClassroomAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for student-to-classroom assignments"""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    classroom_name = serializers.CharField(
        source='classroom.name',
        read_only=True
    )
    
    class Meta:
        model = StudentClassroomAssignment
        fields = [
            'id', 'student', 'student_name', 'classroom', 'classroom_name',
            'academic_year', 'roll_number', 'is_active', 'assigned_date',
            'removed_date', 'removal_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['assigned_date', 'created_at', 'updated_at']


class ParentStudentLinkSerializer(serializers.ModelSerializer):
    """Serializer for parent-student relationships"""
    parent_full_name = serializers.CharField(
        source='parent.get_full_name',
        read_only=True
    )
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = ParentStudentLink
        fields = [
            'id', 'parent', 'parent_full_name', 'student', 'student_name',
            'relationship', 'is_primary', 'receives_progress_reports',
            'can_authorize_absence', 'can_view_grades', 'is_active',
            'linked_date'
        ]
        read_only_fields = ['linked_date']
