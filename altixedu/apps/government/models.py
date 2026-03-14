"""
Government & Compliance Features Models

This module contains models for:
1. Ministry Dashboard - Aggregated real-time school data
2. Audit Logs - Immutable action tracking for compliance
3. Finance Reports - Auto-generated financial statements
4. Compliance Reports - Quarterly accountability reports
5. Offline Mode - Sync queue and conflict resolution
6. Multi-Approver Workflow - Payment approval chain
7. Access Controls - Role-based permissions
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q
import json
from decimal import Decimal


# ============================================================================
# 1. MINISTRY DASHBOARD - Aggregated Real-Time Data
# ============================================================================

class MinistryDashboardAggregation(models.Model):
    """
    Real-time aggregated data for ministry dashboard.
    Updates automatically when school data changes.
    """
    state = models.CharField(max_length=100)
    ministry = models.ForeignKey('schools.Ministry', on_delete=models.CASCADE, null=True, blank=True)
    
    # Deployment metrics
    total_schools = models.IntegerField(default=0)
    schools_live = models.IntegerField(default=0)
    schools_pending = models.IntegerField(default=0)
    avg_deployment_days = models.FloatField(default=0)
    
    # Financial metrics
    total_students = models.IntegerField(default=0)
    total_fees_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_fees_outstanding = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    collection_rate_percentage = models.FloatField(default=0)  # 0-100
    avg_fee_per_student = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Teacher metrics
    total_teachers = models.IntegerField(default=0)
    teachers_active_system = models.IntegerField(default=0)
    teachers_last_7_days = models.IntegerField(default=0)
    avg_teacher_weekly_hours = models.FloatField(default=0)
    total_admin_hours_saved_weekly = models.FloatField(default=0)
    
    # Student metrics
    avg_attendance_rate = models.FloatField(default=0)
    schools_below_attendance_threshold = models.IntegerField(default=0)
    overall_pass_rate = models.FloatField(default=0)
    students_at_risk_count = models.IntegerField(default=0)
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    data_timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['state', 'last_updated']),
            models.Index(fields=['ministry', 'last_updated']),
        ]
    
    def __str__(self):
        return f"Ministry Dashboard {self.state} - {self.data_timestamp}"


class MinistryDashboardAlert(models.Model):
    """Critical, warning, and success alerts for ministry dashboard."""
    
    ALERT_LEVELS = [
        ('critical', 'Critical - Requires Immediate Action'),
        ('warning', 'Warning - Needs Attention'),
        ('success', 'Success - Positive Indicator'),
    ]
    
    dashboard = models.ForeignKey(MinistryDashboardAggregation, on_delete=models.CASCADE, related_name='alerts')
    level = models.CharField(max_length=10, choices=ALERT_LEVELS)
    title = models.CharField(max_length=255)
    description = models.TextField()
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True)
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('collection', 'Collection Rate'),
            ('attendance', 'Attendance'),
            ('deployment', 'Deployment'),
            ('teacher_engagement', 'Teacher Engagement'),
            ('performance', 'Student Performance'),
        ]
    )
    metric_value = models.FloatField()
    threshold = models.FloatField()
    action_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_level_display()}: {self.title}"


# ============================================================================
# 2. AUDIT LOGS - Immutable Action Tracking
# ============================================================================

class AuditLog(models.Model):
    """
    Immutable audit trail of all system actions.
    Required for government compliance and fraud prevention.
    """
    
    ACTION_TYPES = [
        # User actions
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('user_create', 'User Created'),
        ('user_update', 'User Updated'),
        ('user_delete', 'User Deleted'),
        
        # School data
        ('student_create', 'Student Created'),
        ('student_update', 'Student Updated'),
        ('student_delete', 'Student Deleted'),
        ('grade_create', 'Grade Created'),
        ('grade_update', 'Grade Updated'),
        ('attendance_mark', 'Attendance Marked'),
        
        # Financial actions (CRITICAL)
        ('fee_create', 'Fee Created'),
        ('fee_update', 'Fee Updated'),
        ('fee_delete', 'Fee Deleted'),
        ('payment_create', 'Payment Created'),
        ('payment_update', 'Payment Updated'),
        ('payment_approve', 'Payment Approved'),
        ('payment_reject', 'Payment Rejected'),
        ('expense_create', 'Expense Created'),
        ('expense_approve', 'Expense Approved'),
        
        # Admin actions
        ('permission_grant', 'Permission Granted'),
        ('permission_revoke', 'Permission Revoked'),
        ('role_change', 'User Role Changed'),
        ('school_settings_update', 'School Settings Updated'),
    ]
    
    # WHO took the action
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    user_email = models.EmailField()  # Snapshot for audit trail
    user_role = models.CharField(max_length=50)  # Snapshot
    user_school = models.ForeignKey('schools.School', on_delete=models.SET_NULL, null=True, blank=True)
    
    # WHAT action
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    action_description = models.TextField()
    
    # ON WHAT
    content_type = models.CharField(max_length=100)  # Model name (Student, Fee, etc)
    object_id = models.BigIntegerField()  # ID of affected object
    object_name = models.CharField(max_length=255)  # Human-readable name
    
    # CHANGE DETAILS
    before_value = models.JSONField(null=True, blank=True)  # Before state
    after_value = models.JSONField(null=True, blank=True)   # After state
    changed_fields = models.JSONField(default=list, blank=True)  # List of field names changed
    
    # ENVIRONMENT
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=100, blank=True)  # For tracing
    
    # APPROVAL CHAIN (for financial actions)
    approval_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='approved'
    )
    approval_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_actions')
    approval_timestamp = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # TIMESTAMPS (immutable)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # When action happened
    logged_at = models.DateTimeField(auto_now_add=True)  # When logged (should equal created_at)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['object_id', 'content_type']),
            models.Index(fields=['user_school', 'created_at']),
            models.Index(fields=['approval_status', 'created_at']),
        ]
        # Make table append-only (no updates/deletes)
        permissions = [
            ('audit_log_export', 'Can export audit logs'),
            ('audit_log_delete_old', 'Can delete audit logs older than 7 years'),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} by {self.user_email} on {self.created_at}"
    
    def save(self, *args, **kwargs):
        # SECURITY: Prevent updates to existing audit logs
        if self.pk:
            raise ValueError("Audit logs cannot be updated (append-only)")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # SECURITY: Prevent deletion (append-only)
        # Exception: Only system can delete logs older than 7 years for storage
        from datetime import timedelta
        if (timezone.now() - self.created_at).days < 2555:  # 7 years
            raise ValueError("Cannot delete audit logs less than 7 years old")
        super().delete(*args, **kwargs)


# ============================================================================
# 3. FINANCE REPORTS - Auto-Generated Financial Statements
# ============================================================================

class FinanceReport(models.Model):
    """
    Auto-generated financial statements for schools and ministries.
    """
    
    REPORT_TYPES = [
        ('income_statement', 'Income Statement'),
        ('variance_analysis', 'Budget vs Actual'),
        ('fee_status', 'Student Fee Status'),
        ('cash_flow', 'Cash Flow Analysis'),
    ]
    
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='finance_reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    
    # Time period
    start_date = models.DateField()
    end_date = models.DateField()
    period_name = models.CharField(max_length=100)  # "March 2024", "Q1 2024"
    
    # Income Statement Data
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    school_fees_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    government_subvention = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    salary_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    utilities_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    maintenance_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    supplies_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    net_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Budget variance
    budgeted_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    income_variance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    income_variance_percent = models.FloatField(default=0)
    
    budgeted_expenses = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    expense_variance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    expense_variance_percent = models.FloatField(default=0)
    
    # Additional metrics
    expenses_by_category = models.JSONField(null=True, blank=True)  # Category -> amount
    fee_collection_percentage = models.FloatField(default=0)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Export
    pdf_file = models.FileField(upload_to='reports/finance/', null=True, blank=True)
    excel_file = models.FileField(upload_to='reports/finance/', null=True, blank=True)
    
    class Meta:
        ordering = ['-end_date']
        unique_together = ['school', 'report_type', 'start_date', 'end_date']
    
    def __str__(self):
        return f"{self.school.name} - {self.get_report_type_display()} ({self.period_name})"


# ============================================================================
# 4. COMPLIANCE REPORTS - Quarterly Accountability
# ============================================================================

class ComplianceReport(models.Model):
    """
    Quarterly compliance reports for government submission.
    """
    
    REPORT_STATUS = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='compliance_reports')
    state = models.CharField(max_length=100)  # For ministry aggregation
    quarter = models.IntegerField(choices=[(1, 'Q1'), (2, 'Q2'), (3, 'Q3'), (4, 'Q4')])
    year = models.IntegerField()
    
    # Enrollment data
    total_enrolled_students = models.IntegerField()
    total_enrolled_teachers = models.IntegerField()
    
    # Attendance metrics
    avg_student_attendance = models.FloatField()  # 0-100
    avg_teacher_attendance = models.FloatField()  # 0-100
    attendance_trend = models.CharField(max_length=20, default='stable')  # up, down, stable
    
    # Academic performance
    pass_rate_percentage = models.FloatField()  # 0-100
    performance_trend = models.CharField(max_length=20, default='stable')  # up, down, stable
    
    # Finance data
    budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    actual_spend = models.DecimalField(max_digits=15, decimal_places=2)
    spend_variance_percent = models.FloatField()
    fund_utilization_rate = models.FloatField()  # 0-100
    
    # Infrastructure & resources
    classrooms_count = models.IntegerField()
    working_desks_count = models.IntegerField()
    library_books_count = models.IntegerField()
    it_resources_count = models.IntegerField()
    
    # Programs & initiatives
    special_needs_students = models.IntegerField()
    girl_child_support_programs = models.BooleanField()
    teacher_training_hours = models.FloatField()
    
    # Challenges & recommendations
    key_challenges = models.TextField()  # Narrative
    recommendations = models.TextField()  # Auto-generated + manual
    
    # Submission status
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='draft')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='compliance_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Export
    pdf_file = models.FileField(upload_to='reports/compliance/', null=True, blank=True)
    
    class Meta:
        ordering = ['-year', '-quarter']
        unique_together = ['school', 'quarter', 'year']
    
    def __str__(self):
        return f"{self.school.name} - Q{self.quarter} {self.year}"


# ============================================================================
# 5. OFFLINE MODE - Sync Queue & Conflict Resolution
# ============================================================================

class OfflineSyncQueue(models.Model):
    """
    Queues offline changes for sync when device comes online.
    Handles conflict resolution and retry logic.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Sync'),
        ('syncing', 'Currently Syncing'),
        ('synced', 'Successfully Synced'),
        ('conflict', 'Conflict Detected'),
        ('failed', 'Failed - Retry'),
        ('resolved', 'Conflict Resolved'),
    ]
    
    # User & Device
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offline_syncs')
    device_id = models.CharField(max_length=255)  # Unique device identifier
    
    # What data was changed
    content_type = models.CharField(max_length=100)  # Model name
    object_id = models.BigIntegerField()
    object_name = models.CharField(max_length=255)
    
    # The action
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete'),
        ]
    )
    
    # Device changes
    device_data = models.JSONField()  # What user changed locally
    server_data = models.JSONField(null=True, blank=True)  # Current server state (if conflict)
    merged_data = models.JSONField(null=True, blank=True)  # Resolved state
    
    # Conflict detection
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    conflict_detected = models.BooleanField(default=False)
    conflict_reason = models.TextField(blank=True)
    
    # User resolution
    resolution_choice = models.CharField(
        max_length=20,
        choices=[
            ('keep_device', 'Keep Device Version'),
            ('keep_server', 'Keep Server Version'),
            ('merge', 'Merge Both'),
        ],
        null=True,
        blank=True
    )
    resolved_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='conflicts_resolved')
    
    # Sync attempts
    attempt_count = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_locally = models.DateTimeField()  # When user made change (device time)
    queued_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_locally']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['device_id', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.action} {self.object_name} ({self.status})"


# ============================================================================
# 6. MULTI-APPROVER WORKFLOW - Payment Approval Chain
# ============================================================================

class PaymentApprovalThreshold(models.Model):
    """
    School-specific approval thresholds based on country currency.
    Different amounts require different approval levels.
    
    Examples:
    - Nigeria: NGN 500K, 2M, 5M (Naira)
    - Kenya: KES 5M, 20M, 50M (Kenyan Shilling)
    - Ghana: GHS 100K, 500K, 1M (Ghanaian Cedi)
    """
    
    school = models.OneToOneField('schools.School', on_delete=models.CASCADE, related_name='approval_thresholds')
    
    # Get currency from school's country ministry
    country = models.CharField(
        max_length=100,
        help_text="Country (fetched from school's country)"
    )
    currency_code = models.CharField(
        max_length=3,
        help_text="ISO 4217 currency code (NGN, KES, GHS, ZAR, etc.)"
    )
    
    # Tier 1: Bursar can approve up to this
    # Amounts should be set based on country's currency
    tier1_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=500000,
        help_text="Tier 1 threshold (e.g., 500,000 NGN in Nigeria, 5,000,000 KES in Kenya)"
    )
    tier1_approver_role = models.CharField(max_length=50, default='bursar')
    
    # Tier 2: Principal approval needed above Tier 1
    tier2_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=2000000,
        help_text="Tier 2 threshold (e.g., 2,000,000 NGN in Nigeria, 20,000,000 KES in Kenya)"
    )
    tier2_approver_role = models.CharField(max_length=50, default='principal')
    
    # Tier 3: Finance Officer/Government approval needed above Tier 2
    tier3_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=5000000,
        help_text="Tier 3 threshold (e.g., 5,000,000 NGN in Nigeria, 50,000,000 KES in Kenya)"
    )
    tier3_approver_role = models.CharField(max_length=50, default='finance_officer')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.school.name} ({self.currency_code}) - Approval Thresholds"
    
    class Meta:
        verbose_name_plural = "Payment Approval Thresholds"


class PaymentRequest(models.Model):
    """
    Payment request with approval chain.
    """
    
    STATUSES = [
        ('draft', 'Draft'),
        ('pending_tier1', 'Waiting for Bursar Approval'),
        ('pending_tier2', 'Waiting for Principal Approval'),
        ('pending_tier3', 'Waiting for Finance Officer Approval'),
        ('approved', 'Fully Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_TYPES = [
        ('vendor', 'Vendor Payment'),
        ('salary', 'Salary Payment'),
        ('utility', 'Utility Bill'),
        ('maintenance', 'Maintenance'),
        ('supplies', 'Supplies'),
        ('other', 'Other'),
    ]
    
    # Request details
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='payment_requests')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    vendor_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    reason = models.TextField()
    
    # Approvals required based on amount
    requires_tier1_approval = models.BooleanField(default=True)
    requires_tier2_approval = models.BooleanField(default=False)
    requires_tier3_approval = models.BooleanField(default=False)
    
    # Current status
    status = models.CharField(max_length=30, choices=STATUSES, default='draft', db_index=True)
    current_approver_role = models.CharField(max_length=50)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]
    
    def __str__(self):
        return f"Payment Request: {self.vendor_name} - ₦{self.amount}"


class PaymentApproval(models.Model):
    """
    Individual approval steps in the approval chain.
    """
    
    APPROVAL_STATUSES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, related_name='approvals')
    approval_tier = models.IntegerField(choices=[(1, 'Tier 1'), (2, 'Tier 2'), (3, 'Tier 3')])
    required_role = models.CharField(max_length=50)
    
    status = models.CharField(max_length=20, choices=APPROVAL_STATUSES, default='pending')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['approval_tier']
        unique_together = ['payment_request', 'approval_tier']
    
    def __str__(self):
        return f"Payment {self.payment_request.id} - Tier {self.approval_tier} ({self.status})"


# ============================================================================
# 7. ACCESS CONTROLS - Role-Based Permissions
# ============================================================================

class RolePermissionGroup(models.Model):
    """
    Groups of permissions for each role/school combination.
    """
    
    ROLES = [
        ('super_admin', 'Super Admin'),
        ('ministry_admin', 'Ministry Admin'),
        ('school_admin', 'School Admin'),
        ('principal', 'Principal'),
        ('bursar', 'Bursar'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    ]
    
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True)  # Null = system-wide
    role = models.CharField(max_length=50, choices=ROLES)
    
    # Module/Feature access
    can_access_dashboard = models.BooleanField(default=True)
    can_view_students = models.BooleanField(default=False)
    can_edit_students = models.BooleanField(default=False)
    can_view_grades = models.BooleanField(default=False)
    can_edit_grades = models.BooleanField(default=False)
    can_view_attendance = models.BooleanField(default=False)
    can_edit_attendance = models.BooleanField(default=False)
    can_view_finances = models.BooleanField(default=False)
    can_edit_finances = models.BooleanField(default=False)
    can_approve_payments = models.BooleanField(default=False)
    can_view_audit_logs = models.BooleanField(default=False)
    can_export_reports = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_view_ministry_dashboard = models.BooleanField(default=False)
    # School management
    can_view_school_profile = models.BooleanField(default=False)
    can_edit_school_profile = models.BooleanField(default=False)  # Name, address, contact info
    can_edit_school_settings = models.BooleanField(default=False)  # Fees, configuration, policies
    
    # Personnel management
    can_manage_teachers = models.BooleanField(default=False)  # Add/edit/delete teachers
    can_manage_bursars = models.BooleanField(default=False)  # Add/edit/delete bursars
    can_manage_staff = models.BooleanField(default=False)  # Add/edit/delete all staff
    
    # Class & Assignment management
    can_manage_classrooms = models.BooleanField(default=False)  # Create/edit classes
    can_assign_teachers_to_class = models.BooleanField(default=False)  # Assign teachers to classes
    can_assign_students_to_class = models.BooleanField(default=False)  # Move students between classes
    
    # Parent & Student linking
    can_link_parent_student = models.BooleanField(default=False)  # Link parents to students
    can_manage_parent_records = models.BooleanField(default=False)  # Add/edit parent info
    
    # Scope of access
    can_see_all_schools = models.BooleanField(default=False)  # Ministry admin only
    can_see_all_students = models.BooleanField(default=False)
    can_see_all_teachers = models.BooleanField(default=False)
    
    # Data filtering rules (JSON)
    # Example: {"schools": [1, 2, 3], "classrooms": [5, 6], "subjects": [10, 11]}
    allowed_objects = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'role']
    
    def __str__(self):
        school_name = self.school.name if self.school else "System-wide"
        return f"{school_name} - {self.get_role_display()}"


class UserAccessLog(models.Model):
    """
    Track which users accessed what data and when.
    Useful for security audits.
    """
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='access_logs')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE)
    
    # Resource accessed
    resource_type = models.CharField(max_length=50)  # students, grades, finances, etc
    resource_id = models.BigIntegerField()
    resource_name = models.CharField(max_length=255)
    
    # Access details
    action = models.CharField(
        max_length=20,
        choices=[('view', 'View'), ('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')]
    )
    was_allowed = models.BooleanField(default=True)
    denial_reason = models.CharField(max_length=255, blank=True)
    
    # Environment
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    accessed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'accessed_at']),
            models.Index(fields=['was_allowed', 'accessed_at']),
        ]
    
    def __str__(self):
        action_word = f"{self.action} {self.resource_type}"
        allowed = "✓" if self.was_allowed else "✗"
        return f"{allowed} {self.user.email} {action_word}"
