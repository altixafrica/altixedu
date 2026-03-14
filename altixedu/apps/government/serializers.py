"""
Serializers for Government Features APIs
"""

from rest_framework import serializers
from .models import (
    MinistryDashboardAggregation,
    MinistryDashboardAlert,
    AuditLog,
    FinanceReport,
    ComplianceReport,
    OfflineSyncQueue,
    PaymentRequest,
    PaymentApproval,
    PaymentApprovalThreshold,
    RolePermissionGroup,
    UserAccessLog,
)
from django.contrib.auth.models import User


class MinistryDashboardAlertSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = MinistryDashboardAlert
        fields = [
            'id', 'level', 'level_display', 'title', 'description',
            'metric_type', 'metric_type_display', 'metric_value', 'threshold',
            'school', 'action_url', 'created_at'
        ]
        read_only_fields = ['created_at']


class MinistryDashboardSerializer(serializers.ModelSerializer):
    """Serializes aggregated ministry dashboard data."""
    
    alerts = MinistryDashboardAlertSerializer(many=True, read_only=True)
    admin_hours_saved_yearly = serializers.SerializerMethodField()
    admin_value_saved_yearly = serializers.SerializerMethodField()
    
    class Meta:
        model = MinistryDashboardAggregation
        fields = [
            'id', 'state', 'ministry',
            # Deployment
            'total_schools', 'schools_live', 'schools_pending',
            'avg_deployment_days',
            # Financial
            'total_students', 'total_fees_collected', 'total_fees_outstanding',
            'collection_rate_percentage', 'avg_fee_per_student',
            # Teacher
            'total_teachers', 'teachers_active_system', 'teachers_last_7_days',
            'avg_teacher_weekly_hours', 'total_admin_hours_saved_weekly',
            'admin_hours_saved_yearly', 'admin_value_saved_yearly',
            # Student
            'avg_attendance_rate', 'schools_below_attendance_threshold',
            'overall_pass_rate', 'students_at_risk_count',
            # Metadata
            'alerts', 'last_updated', 'data_timestamp'
        ]
        read_only_fields = ['last_updated', 'data_timestamp']
    
    def get_admin_hours_saved_yearly(self, obj):
        """Calculate yearly admin hours saved (52 weeks)."""
        return round(obj.total_admin_hours_saved_weekly * 52, 2)
    
    def get_admin_value_saved_yearly(self, obj):
        """Calculate yearly monetary value saved (₦25k per hour)."""
        yearly_hours = obj.total_admin_hours_saved_weekly * 52
        value_per_hour = 25000  # ₦25k per admin hour
        return int(yearly_hours * value_per_hour)


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializes audit log entries."""
    
    user_display = serializers.CharField(source='user_email', read_only=True)
    action_display = serializers.CharField(source='get_action_type_display', read_only=True)
    approval_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'user_role', 'user_display',
            'action_type', 'action_display', 'action_description',
            'content_type', 'object_id', 'object_name',
            'before_value', 'after_value', 'changed_fields',
            'ip_address', 'request_id',
            'approval_status', 'approval_display', 'approval_by', 'approval_timestamp',
            'created_at',
        ]
        read_only_fields = ['created_at', 'logged_at']


class FinanceReportSerializer(serializers.ModelSerializer):
    """Serializes finance reports."""
    
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = FinanceReport
        fields = [
            'id', 'school', 'school_name', 'report_type', 'report_type_display',
            'start_date', 'end_date', 'period_name',
            'total_income', 'school_fees_income', 'government_subvention', 'other_income',
            'total_expenses', 'salary_expenses', 'utilities_expenses',
            'maintenance_expenses', 'supplies_expenses',
            'net_income', 'expenses_by_category', 'fee_collection_percentage',
            'budgeted_income', 'income_variance', 'income_variance_percent',
            'budgeted_expenses', 'expense_variance', 'expense_variance_percent',
            'generated_at', 'pdf_file', 'excel_file',
        ]
        read_only_fields = ['generated_at', 'last_updated', 'net_income']


class ComplianceReportSerializer(serializers.ModelSerializer):
    """Serializes compliance reports."""
    
    quarter_display = serializers.CharField(source='get_quarter_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = ComplianceReport
        fields = [
            'id', 'school', 'school_name', 'state',
            'quarter', 'quarter_display', 'year',
            'total_enrolled_students', 'total_enrolled_teachers',
            'avg_student_attendance', 'avg_teacher_attendance', 'attendance_trend',
            'pass_rate_percentage', 'performance_trend',
            'budgeted_amount', 'actual_spend', 'spend_variance_percent', 'fund_utilization_rate',
            'classrooms_count', 'working_desks_count', 'library_books_count', 'it_resources_count',
            'special_needs_students', 'girl_child_support_programs', 'teacher_training_hours',
            'key_challenges', 'recommendations',
            'status', 'status_display', 'submitted_by', 'submitted_date',
            'approved_by', 'approved_date',
            'created_at', 'updated_at', 'pdf_file',
        ]
        read_only_fields = ['created_at', 'updated_at']


class OfflineSyncQueueSerializer(serializers.ModelSerializer):
    """Serializes offline sync queue items."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = OfflineSyncQueue
        fields = [
            'id', 'user', 'user_email', 'device_id',
            'content_type', 'object_id', 'object_name',
            'action', 'action_display',
            'device_data', 'server_data', 'merged_data',
            'status', 'status_display',
            'conflict_detected', 'conflict_reason',
            'resolution_choice', 'resolved_by_user',
            'attempt_count', 'last_attempt', 'error_message',
            'created_locally', 'queued_at', 'synced_at',
        ]
        read_only_fields = ['queued_at', 'synced_at', 'last_attempt']


class PaymentApprovalThresholdSerializer(serializers.ModelSerializer):
    """Serializes payment approval thresholds."""
    
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = PaymentApprovalThreshold
        fields = [
            'id', 'school', 'school_name',
            'tier1_amount', 'tier1_approver_role',
            'tier2_amount', 'tier2_approver_role',
            'tier3_amount', 'tier3_approver_role',
        ]


class PaymentApprovalSerializer(serializers.ModelSerializer):
    """Serializes individual payment approvals."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tier_display = serializers.CharField(source='get_approval_tier_display', read_only=True)
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    
    class Meta:
        model = PaymentApproval
        fields = [
            'id', 'payment_request', 'approval_tier', 'tier_display',
            'required_role', 'status', 'status_display',
            'approver', 'approver_name', 'approval_notes',
            'approved_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_at']


class PaymentRequestSerializer(serializers.ModelSerializer):
    """Serializes payment requests with full approval chain."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approvals = PaymentApprovalSerializer(many=True, read_only=True)
    
    class Meta:
        model = PaymentRequest
        fields = [
            'id', 'school', 'school_name',
            'payment_type', 'payment_type_display',
            'vendor_name', 'amount', 'currency', 'reason',
            'requires_tier1_approval', 'requires_tier2_approval', 'requires_tier3_approval',
            'status', 'status_display', 'current_approver_role',
            'approvals',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'status']


class RolePermissionGroupSerializer(serializers.ModelSerializer):
    """Serializes role-based permission groups."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = RolePermissionGroup
        fields = [
            'id', 'school', 'school_name', 'role', 'role_display',
            # Module access
            'can_access_dashboard', 'can_view_students', 'can_edit_students',
            'can_view_grades', 'can_edit_grades',
            'can_view_attendance', 'can_edit_attendance',
            'can_view_finances', 'can_edit_finances',
            'can_approve_payments', 'can_view_audit_logs',
            'can_export_reports', 'can_manage_users',
            'can_view_ministry_dashboard',
            # Scope
            'can_see_all_schools', 'can_see_all_students', 'can_see_all_teachers',
            # Object filters
            'allowed_objects',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserAccessLogSerializer(serializers.ModelSerializer):
    """Serializes user access logs."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = UserAccessLog
        fields = [
            'id', 'user', 'user_email', 'school', 'school_name',
            'resource_type', 'resource_id', 'resource_name',
            'action', 'was_allowed', 'denial_reason',
            'ip_address', 'accessed_at',
        ]
        read_only_fields = ['accessed_at']
