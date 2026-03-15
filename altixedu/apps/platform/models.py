from django.db import models
from apps.schools.models import School
from apps.accounts.models import User


class Announcement(models.Model):
    """
    School announcements visible to specific roles.
    """
    
    TARGET_ROLE_CHOICES = (
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('teachers', 'Teachers Only'),
        ('parents', 'Parents Only'),
        ('admin', 'Admin Only'),
    )
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Announcement title"
    )
    
    message = models.TextField(
        help_text="Full announcement message"
    )
    
    target_role = models.CharField(
        max_length=20,
        choices=TARGET_ROLE_CHOICES,
        default='all',
        help_text="Who should see this announcement"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements_created'
    )
    
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin announcement to top of feed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['school', '-created_at']),
            models.Index(fields=['school', 'target_role']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.school.name})"


class AIRiskAlert(models.Model):
    """
    AI-generated risk alerts for students.
    Alerts can be about attendance, grades, assignments, etc.
    """
    
    ALERT_TYPE_CHOICES = (
        ('attendance', 'Attendance'),
        ('grades', 'Grades/Performance'),
        ('assignment', 'Assignment/Homework'),
        ('behavior', 'Behavior'),
        ('health', 'Health'),
        ('other', 'Other'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='ai_risk_alerts'
    )
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='risk_alerts',
        help_text="NULL means school-wide alert"
    )
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        help_text="Type of risk detected"
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text="Alert severity level"
    )
    
    message = models.TextField(
        help_text="Alert message with details"
    )
    
    recommendation = models.TextField(
        null=True,
        blank=True,
        help_text="Recommended action"
    )
    
    is_resolved = models.BooleanField(
        default=False,
        help_text="Mark alert as resolved"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity', '-created_at']
        indexes = [
            models.Index(fields=['school', 'student', '-created_at']),
            models.Index(fields=['school', 'severity', 'is_resolved']),
        ]
    
    def __str__(self):
        student_name = str(self.student) if self.student else "School-wide"
        return f"{self.alert_type.upper()} - {student_name} ({self.severity})"
