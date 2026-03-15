"""
Custom Roles and Advanced Permission System
Allows admins to define custom roles with specific permissions
"""

from django.db import models
from django.contrib.auth.models import Permission
from apps.accounts.models import User
from apps.schools.models import School


class CustomRole(models.Model):
    """
    Custom role definition.
    Schools can create custom roles inheriting from base roles with specific permissions.
    """
    
    BASED_ON_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('bursar', 'Bursar'),
    )
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='custom_roles',
        null=True,
        blank=True,
        help_text="Leave blank for system-wide roles"
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Role inheritance
    based_on = models.CharField(
        max_length=20,
        choices=BASED_ON_CHOICES,
        help_text="Base role this custom role inherits from"
    )
    
    # Specific permissions (override inherited)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text="Select specific permissions for this role"
    )
    
    # Dashboard/UI customization
    dashboard_template = models.CharField(
        max_length=50,
        blank=True,
        help_text="Custom dashboard layout for this role"
    )
    
    visible_modules = models.JSONField(
        default=list,
        blank=True,
        help_text="List of modules visible to this role"
    )
    
    can_manage_users = models.BooleanField(default=False)
    can_manage_finances = models.BooleanField(default=False)
    can_manage_academics = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    can_export_data = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_roles'
    )
    
    class Meta:
        unique_together = ('school', 'name')
        ordering = ['school', 'name']
    
    def __str__(self):
        return f"{self.name} (based on {self.based_on})"


class RoleUserAssignment(models.Model):
    """
    Assign custom roles to users.
    A user can have multiple custom roles if needed.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_role_assignments'
    )
    
    role = models.ForeignKey(
        CustomRole,
        on_delete=models.CASCADE
    )
    
    # When assignment is active
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles',
        limit_choices_to={'role': 'admin'}
    )
    
    # When assignment ends
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Role assignment expiration date"
    )
    
    class Meta:
        unique_together = ('user', 'role')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.name}"


class StudentClassroomAssignment(models.Model):
    """
    Enhanced student-to-classroom assignment with academic year tracking
    and roll number management.
    """
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='classroom_assignments'
    )
    
    classroom = models.ForeignKey(
        'academics.Classroom',
        on_delete=models.CASCADE,
        related_name='student_assignments'
    )
    
    # Academic year (e.g., 2024-2025)
    academic_year = models.CharField(
        max_length=20,
        help_text="Academic year (e.g., 2024-2025)"
    )
    
    # Roll number in the classroom
    roll_number = models.IntegerField(
        help_text="Student's roll number/seat number in the classroom"
    )
    
    # Assignment status
    is_active = models.BooleanField(default=True)
    
    # Dates
    assigned_date = models.DateField(auto_now_add=True)
    removed_date = models.DateField(null=True, blank=True)
    
    # Reason for removal (if removed)
    removal_reason = models.CharField(
        max_length=200,
        blank=True,
        choices=[
            ('promoted', 'Promoted'),
            ('demoted', 'Demoted'),
            ('transferred', 'Transferred'),
            ('graduated', 'Graduated'),
            ('dropped', 'Dropped Out'),
            ('other', 'Other'),
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'classroom', 'academic_year')
        ordering = ['classroom', 'roll_number']
        indexes = [
            models.Index(fields=['classroom', 'academic_year']),
            models.Index(fields=['student', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.student} in {self.classroom} ({self.academic_year})"


class ParentStudentLink(models.Model):
    """
    Enhanced parent-student linking with multiple relationships and primary contact.
    """
    
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_links',
        limit_choices_to={'role': 'parent'}
    )
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='parent_links'
    )
    
    relationship = models.CharField(
        max_length=50,
        choices=[
            ('mother', 'Mother'),
            ('father', 'Father'),
            ('guardian', 'Guardian'),
            ('grandparent', 'Grandparent'),
            ('sibling', 'Sibling'),
            ('other', 'Other'),
        ]
    )
    
    # Primary contact for student
    is_primary = models.BooleanField(default=False)
    
    # Contact permissions
    receives_progress_reports = models.BooleanField(default=True)
    can_authorize_absence = models.BooleanField(default=False)
    can_view_grades = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    linked_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('parent', 'student')
        ordering = ['-is_primary', 'parent']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['student', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.parent.get_full_name()} ({self.relationship}) -> {self.student}"
