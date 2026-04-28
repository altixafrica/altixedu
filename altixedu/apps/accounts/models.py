from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.schools.models import School


class User(AbstractUser):
    ROLE_CHOICES = (
        # SCHOOL-LEVEL ROLES (user.school required)
        ('admin', 'School Admin / Principal'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('bursar', 'School Bursar / Finance Officer'),
        
        # GOVERNMENT-LEVEL ROLES (user.ministry assigned)
        ('ministry_admin', 'Ministry Admin'),
        
        # PLATFORM-LEVEL ROLES (system-wide)
        ('superadmin', 'Super Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
        help_text="NULL for superadmin/ministry_admin, required for other roles"
    )
    ministry = models.ForeignKey(
        'schools.Ministry',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='admin_users',
        help_text="Required for ministry_admin role (restricts to their state)"
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Optional phone number"
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        help_text="User profile photo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('school', 'email')]  # Email unique per school

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


from .role_models import CustomRole, ParentStudentLink, RoleUserAssignment, StudentClassroomAssignment  # noqa: E402,F401
