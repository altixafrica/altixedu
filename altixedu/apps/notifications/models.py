from django.db import models
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.schools.models import School
from apps.students.models import Student


class Message(models.Model):
    """Internal messaging system for school communication."""
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: if message is about a specific student"
    )

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} | Read: {self.read}"


class StudentAIInsights(models.Model):
    """AI-powered insights for student performance and attendance tracking."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='ai_insights'
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    # Risk scores (0-1 scale)
    attendance_risk = models.FloatField(default=0.0)
    performance_risk = models.FloatField(default=0.0)
    overall_risk = models.FloatField(default=0.0)  # Average of both
    
    # Flag details
    low_attendance = models.BooleanField(default=False)
    low_performance = models.BooleanField(default=False)
    flagged_subjects = models.JSONField(default=list)
    
    # Last calculated metrics
    attendance_percentage = models.FloatField(default=0.0)
    average_grade = models.FloatField(default=0.0)
    days_absent = models.IntegerField(default=0)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-overall_risk']

    def __str__(self):
        return f"{self.student} - Overall Risk: {self.overall_risk:.2f}"
    
    def calculate_attendance_risk(self, school_settings=None):
        """
        Calculate attendance risk based on recent attendance.
        Risk = 1.0 (high risk) when attendance < threshold
        Risk = 0.0 (low risk) when attendance >= threshold
        """
        from apps.attendance.models import Attendance
        
        # Get school settings
        if not school_settings:
            school_settings = getattr(self.school, 'settings', None)
        threshold = school_settings.attendance_threshold if school_settings else 75
        
        # Calculate attendance for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        attendance_records = Attendance.objects.filter(
            student=self.student,
            date__gte=thirty_days_ago.date()
        )
        
        if not attendance_records.exists():
            return 0.5  # Unknown risk if no recent data
        
        total_records = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        attendance_pct = (present_count / total_records * 100) if total_records > 0 else 0
        
        self.attendance_percentage = attendance_pct
        self.days_absent = total_records - present_count
        self.low_attendance = attendance_pct < threshold
        
        # Risk calculation: inversely proportional to attendance
        if attendance_pct >= threshold:
            return 0.0  # Low risk
        elif attendance_pct < 50:
            return 1.0  # High risk
        else:
            # Linear scale between 50-75%
            return (threshold - attendance_pct) / (threshold - 50)
    
    def calculate_performance_risk(self, school_settings=None):
        """
        Calculate performance risk based on exam results/grades.
        Risk = 1.0 (high risk) when grade < threshold
        Risk = 0.0 (low risk) when grade >= threshold
        """
        from apps.academics.models import ExamResult
        
        if not school_settings:
            school_settings = getattr(self.school, 'settings', None)
        threshold = school_settings.performance_threshold if school_settings else 70.0
        
        # Get latest exam results (last 60 days)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        exam_results = ExamResult.objects.filter(
            student=self.student,
            created_at__gte=sixty_days_ago
        )
        
        if not exam_results.exists():
            return 0.3  # Moderate risk if no recent exam data
        
        avg_grade = exam_results.aggregate(Avg('score'))['score__avg'] or 0
        self.average_grade = avg_grade
        self.low_performance = avg_grade < threshold
        
        # Identify weak subjects
        flagged_subjects_list = []
        weak_subject_results = exam_results.filter(score__lt=threshold).values('subject__name').distinct()
        for item in weak_subject_results:
            flagged_subjects_list.append(item['subject__name'])
        self.flagged_subjects = flagged_subjects_list
        
        # Risk calculation: inversely proportional to performance
        if avg_grade >= threshold:
            return 0.0  # Low risk
        elif avg_grade < 50:
            return 1.0  # High risk
        else:
            # Linear scale between 50-threshold
            return (threshold - avg_grade) / (threshold - 50)
    
    def calculate_all_risks(self):
        """Calculate both risks and overall risk score."""
        school_settings = getattr(self.school, 'settings', None)
        
        self.attendance_risk = self.calculate_attendance_risk(school_settings)
        self.performance_risk = self.calculate_performance_risk(school_settings)
        
        # Overall risk is weighted average (60% performance, 40% attendance)
        self.overall_risk = (self.performance_risk * 0.6) + (self.attendance_risk * 0.4)
        
        self.calculated_at = timezone.now()
        self.save()
        
        return self.overall_risk
    
    def get_risk_level(self):
        """Return human-readable risk level."""
        if self.overall_risk >= 0.7:
            return 'CRITICAL'
        elif self.overall_risk >= 0.5:
            return 'HIGH'
        elif self.overall_risk >= 0.3:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def get_recommendations(self):
        """Generate actionable recommendations based on risks."""
        recommendations = []
        
        if self.low_attendance:
            recommendations.append({
                'type': 'attendance',
                'message': f'Student absent {self.days_absent} days in last 30 days',
                'action': 'Contact parent to discuss attendance'
            })
        
        if self.low_performance:
            recommendations.append({
                'type': 'performance',
                'message': f'Average grade ({self.average_grade:.1f}) below threshold ({70.0})',
                'action': 'Recommend tutoring or additional support'
            })
        
        if self.flagged_subjects:
            recommendations.append({
                'type': 'subjects',
                'message': f'Struggling in: {", ".join(self.flagged_subjects)}',
                'action': 'Increase focus on these subjects'
            })
        
        return recommendations


class SchoolSetting(models.Model):
    """Per-school configuration and branding."""
    school = models.OneToOneField(
        School,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='settings'
    )
    
    # Branding (store logo as URL string instead of ImageField to avoid Pillow dependency)
    logo_url = models.URLField(null=True, blank=True, help_text="School logo URL")
    primary_color = models.CharField(max_length=7, default='#003366')
    secondary_color = models.CharField(max_length=7, default='#006699')
    
    # Academic Settings
    school_year = models.CharField(max_length=10, default='2024-2025')
    attendance_threshold = models.IntegerField(default=75)
    performance_threshold = models.FloatField(default=70.0)
    
    # Portal Configuration
    enable_parent_portal = models.BooleanField(default=True)
    enable_student_portal = models.BooleanField(default=True)
    enable_teacher_portal = models.BooleanField(default=True)
    
    # Notifications
    notification_email = models.EmailField(null=True, blank=True)
    enable_email_alerts = models.BooleanField(default=True)
    enable_sms_alerts = models.BooleanField(default=False)
    
    # Fee Configuration
    default_fee_structure = models.JSONField(
        default=list,
        help_text="Default fee items: [{'name': 'Tuition', 'amount': 5000}, ...]"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.school.name}"


class RoleSetting(models.Model):
    """Per-role and per-school settings for fine-grained configuration."""
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
        ('bursar', 'Bursar')
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="NULL for superadmin global settings"
    )
    key = models.CharField(max_length=100)
    value = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('role', 'school', 'key')
        ordering = ['role', 'key']

    def __str__(self):
        school_name = self.school.name if self.school else "Global"
        return f"{self.role} - {self.key} ({school_name})"


class NotificationPreference(models.Model):
    """User notification preferences for email, SMS, and in-app notifications."""
    
    NOTIFICATION_TYPES = [
        ('announcement', 'Announcements'),
        ('message', 'Direct Messages'),
        ('grade', 'Grade Updates'),
        ('attendance', 'Attendance Alerts'),
        ('fee', 'Fee Reminders'),
        ('schedule', 'Schedule Changes'),
        ('system', 'System Updates'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Channel preferences (global)
    email_enabled = models.BooleanField(default=True, help_text="Receive email notifications")
    sms_enabled = models.BooleanField(default=False, help_text="Receive SMS notifications")
    in_app_enabled = models.BooleanField(default=True, help_text="Receive in-app notifications")
    
    # Notification type preferences (per type, all channels)
    announcements_enabled = models.BooleanField(default=True)
    messages_enabled = models.BooleanField(default=True)
    grades_enabled = models.BooleanField(default=True)
    attendance_enabled = models.BooleanField(default=True)
    fees_enabled = models.BooleanField(default=True)
    schedule_enabled = models.BooleanField(default=True)
    system_enabled = models.BooleanField(default=False)
    
    # Advanced options
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text="Do not send notifications before this time"
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text="Do not send notifications after this time"
    )
    
    # Digest options
    digest_frequency = models.CharField(
        max_length=20,
        default='realtime',
        choices=[
            ('realtime', 'Real-time'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('never', 'Never'),
        ],
        help_text="How often to receive notification digests"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Notification Preferences"
    
    def __str__(self):
        return f"Notification Preferences for {self.user.username}"
    
    def should_send_notification(self, notification_type, channel='email'):
        """
        Check if notification should be sent based on user preferences.
        
        Args:
            notification_type: str - Type of notification (announcement, message, grade, etc.)
            channel: str - Channel to send on (email, sms, in_app)
        
        Returns:
            bool - Whether to send this notification
        """
        # Check channel enabled
        if channel == 'email' and not self.email_enabled:
            return False
        elif channel == 'sms' and not self.sms_enabled:
            return False
        elif channel == 'in_app' and not self.in_app_enabled:
            return False
        
        # Check notification type enabled
        type_attr = f"{notification_type}_enabled"
        if hasattr(self, type_attr):
            if not getattr(self, type_attr):
                return False
        
        # Check quiet hours (skip for sms and urgent messages)
        if channel == 'email' and self.quiet_hours_start and self.quiet_hours_end:
            current_time = timezone.now().time()
            if self.quiet_hours_start <= current_time <= self.quiet_hours_end:
                return False
        
        return True
    
    def enable_all(self):
        """Enable all notifications."""
        self.email_enabled = True
        self.sms_enabled = True
        self.in_app_enabled = True
        self.announcements_enabled = True
        self.messages_enabled = True
        self.grades_enabled = True
        self.attendance_enabled = True
        self.fees_enabled = True
        self.schedule_enabled = True
        self.system_enabled = True
        self.save()
    
    def disable_all(self):
        """Disable all notifications."""
        self.email_enabled = False
        self.sms_enabled = False
        self.in_app_enabled = False
        self.announcements_enabled = False
        self.messages_enabled = False
        self.grades_enabled = False
        self.attendance_enabled = False
        self.fees_enabled = False
        self.schedule_enabled = False
        self.system_enabled = False
        self.save()
