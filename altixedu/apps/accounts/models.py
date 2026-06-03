from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import pyotp
import secrets
import string
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


class UserTwoFactor(models.Model):
    """
    Two-Factor Authentication storage for users.
    Supports TOTP (Time-based One-Time Password) with backup codes.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='two_factor'
    )
    
    # TOTP secret key
    secret_key = models.CharField(max_length=255, help_text="TOTP secret")
    
    # 2FA enabled/disabled
    is_enabled = models.BooleanField(default=False)
    
    # Backup codes (JSON list)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enabled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "User Two-Factor Auth"
    
    def __str__(self):
        return f"2FA for {self.user.get_full_name()}"
    
    @staticmethod
    def generate_secret():
        """Generate new TOTP secret"""
        return pyotp.random_base32()
    
    def get_totp(self):
        """Get TOTP instance for user"""
        return pyotp.TOTP(self.secret_key)
    
    def verify_totp(self, token):
        """Verify TOTP token (with 1-step window for drift)"""
        totp = self.get_totp()
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def generate_backup_codes(count=10):
        """Generate backup codes"""
        return [
            ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            for _ in range(count)
        ]
    
    def verify_backup_code(self, code):
        """Verify and consume backup code"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False


from .role_models import CustomRole, ParentStudentLink, RoleUserAssignment, StudentClassroomAssignment  # noqa: E402,F401
