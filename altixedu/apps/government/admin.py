"""
Django Admin Configuration for Government Features
"""

from django.contrib import admin
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


# ============================================================================
# 1. MINISTRY DASHBOARD ADMIN
# ============================================================================

class MinistryDashboardAlertInline(admin.TabularInline):
    model = MinistryDashboardAlert
    extra = 0
    readonly_fields = ['created_at']
    fields = ['level', 'title', 'metric_type', 'metric_value', 'threshold', 'school']


@admin.register(MinistryDashboardAggregation)
class MinistryDashboardAdmin(admin.ModelAdmin):
    list_display = ['state', 'total_schools', 'schools_live', 'collection_rate_percentage',
                   'total_students', 'last_updated']
    list_filter = ['state', 'last_updated']
    search_fields = ['state', 'ministry__name']
    readonly_fields = ['last_updated', 'data_timestamp']
    inlines = [MinistryDashboardAlertInline]
    
    fieldsets = (
        ('Location', {
            'fields': ('state', 'ministry')
        }),
        ('Deployment Metrics', {
            'fields': ('total_schools', 'schools_live', 'schools_pending', 'avg_deployment_days')
        }),
        ('Financial Metrics', {
            'fields': ('total_students', 'total_fees_collected', 'total_fees_outstanding',
                      'collection_rate_percentage', 'avg_fee_per_student')
        }),
        ('Teacher Metrics', {
            'fields': ('total_teachers', 'teachers_active_system', 'teachers_last_7_days',
                      'avg_teacher_weekly_hours', 'total_admin_hours_saved_weekly')
        }),
        ('Student Metrics', {
            'fields': ('avg_attendance_rate', 'schools_below_attendance_threshold',
                      'overall_pass_rate', 'students_at_risk_count')
        }),
        ('Metadata', {
            'fields': ('last_updated', 'data_timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(MinistryDashboardAlert)
class MinistryDashboardAlertAdmin(admin.ModelAdmin):
    list_display = ['level', 'title', 'metric_type', 'school', 'created_at']
    list_filter = ['level', 'metric_type', 'created_at']
    search_fields = ['title', 'school__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


# ============================================================================
# 2. AUDIT LOGS ADMIN
# ============================================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['get_action_display', 'user_email', 'user_role', 'created_at',
                   'approval_status', 'object_name']
    list_filter = ['action_type', 'approval_status', 'created_at', 'user_school']
    search_fields = ['user_email', 'object_name', 'action_description']
    readonly_fields = ['created_at', 'logged_at', 'user_email']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Action Details', {
            'fields': ('action_type', 'action_description', 'user', 'user_email', 'user_role')
        }),
        ('Affected Object', {
            'fields': ('content_type', 'object_id', 'object_name')
        }),
        ('Changes', {
            'fields': ('before_value', 'after_value', 'changed_fields')
        }),
        ('Environment', {
            'fields': ('ip_address', 'user_agent', 'request_id')
        }),
        ('Approval Chain', {
            'fields': ('approval_status', 'approval_by', 'approval_timestamp', 'approval_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'logged_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        if obj and (obj.created_at - __import__('django.utils.timezone', fromlist=['now']).now()).days > 2555:
            return request.user.is_superuser
        return False
    
    def get_action_display(self, obj):
        return obj.get_action_type_display()
    get_action_display.short_description = 'Action Type'


# ============================================================================
# 3. FINANCE REPORTS ADMIN
# ============================================================================

@admin.register(FinanceReport)
class FinanceReportAdmin(admin.ModelAdmin):
    list_display = ['school', 'report_type', 'period_name', 'net_income', 'fee_collection_percentage',
                   'generated_at']
    list_filter = ['report_type', 'start_date', 'school']
    search_fields = ['school__name', 'period_name']
    readonly_fields = ['generated_at', 'last_updated', 'net_income']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Report Info', {
            'fields': ('school', 'report_type', 'start_date', 'end_date', 'period_name')
        }),
        ('Income', {
            'fields': ('total_income', 'school_fees_income', 'government_subvention', 'other_income')
        }),
        ('Expenses', {
            'fields': ('total_expenses', 'salary_expenses', 'utilities_expenses',
                      'maintenance_expenses', 'supplies_expenses', 'expenses_by_category')
        }),
        ('Net', {
            'fields': ('net_income',)
        }),
        ('Variance Analysis', {
            'fields': ('budgeted_income', 'income_variance', 'income_variance_percent',
                      'budgeted_expenses', 'expense_variance', 'expense_variance_percent'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('fee_collection_percentage',)
        }),
        ('Files', {
            'fields': ('pdf_file', 'excel_file')
        }),
        ('Metadata', {
            'fields': ('generated_by', 'generated_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# 4. COMPLIANCE REPORTS ADMIN
# ============================================================================

@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ['school', 'quarter', 'year', 'status', 'pass_rate_percentage', 'submitted_date']
    list_filter = ['status', 'year', 'quarter', 'state']
    search_fields = ['school__name', 'state']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('School & Period', {
            'fields': ('school', 'state', 'year', 'quarter')
        }),
        ('Enrollment', {
            'fields': ('total_enrolled_students', 'total_enrolled_teachers')
        }),
        ('Attendance', {
            'fields': ('avg_student_attendance', 'avg_teacher_attendance', 'attendance_trend')
        }),
        ('Academic Performance', {
            'fields': ('pass_rate_percentage', 'performance_trend')
        }),
        ('Finance', {
            'fields': ('budgeted_amount', 'actual_spend', 'spend_variance_percent', 'fund_utilization_rate')
        }),
        ('Infrastructure', {
            'fields': ('classrooms_count', 'working_desks_count', 'library_books_count', 'it_resources_count')
        }),
        ('Programs', {
            'fields': ('special_needs_students', 'girl_child_support_programs', 'teacher_training_hours')
        }),
        ('Analysis', {
            'fields': ('key_challenges', 'recommendations')
        }),
        ('Submission', {
            'fields': ('status', 'submitted_by', 'submitted_date', 'approved_by', 'approved_date')
        }),
        ('Files', {
            'fields': ('pdf_file',)
        }),
    )
    
    actions = ['approve_reports', 'reject_reports']
    
    def approve_reports(self, request, queryset):
        updated = queryset.update(status='approved', approved_by=request.user,
                                 approved_date=__import__('django.utils.timezone', fromlist=['now']).now())
        self.message_user(request, f'{updated} reports approved.')
    
    def reject_reports(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} reports rejected.')


# ============================================================================
# 5. OFFLINE SYNC ADMIN
# ============================================================================

@admin.register(OfflineSyncQueue)
class OfflineSyncQueueAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_id', 'action', 'status', 'conflict_detected', 'created_locally']
    list_filter = ['status', 'action', 'conflict_detected', 'device_id']
    search_fields = ['user__email', 'object_name', 'device_id']
    readonly_fields = ['queued_at', 'synced_at', 'created_locally']
    date_hierarchy = 'created_locally'
    
    fieldsets = (
        ('User & Device', {
            'fields': ('user', 'device_id')
        }),
        ('Data', {
            'fields': ('content_type', 'object_id', 'object_name', 'action')
        }),
        ('Changes', {
            'fields': ('device_data', 'server_data', 'merged_data')
        }),
        ('Conflict Resolution', {
            'fields': ('conflict_detected', 'conflict_reason', 'resolution_choice', 'resolved_by_user')
        }),
        ('Sync Status', {
            'fields': ('status', 'attempt_count', 'last_attempt', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_locally', 'queued_at', 'synced_at')
        }),
    )
    
    actions = ['mark_synced', 'clear_failed']
    
    def mark_synced(self, request, queryset):
        queryset.update(status='synced')
        self.message_user(request, 'Items marked as synced.')
    
    def clear_failed(self, request, queryset):
        queryset.filter(status='failed').delete()
        self.message_user(request, 'Failed items cleared.')


# ============================================================================
# 6. PAYMENT APPROVALS ADMIN
# ============================================================================

class PaymentApprovalInline(admin.TabularInline):
    model = PaymentApproval
    extra = 0
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    fields = ['approval_tier', 'required_role', 'status', 'approver', 'approved_at']


@admin.register(PaymentApprovalThreshold)
class PaymentApprovalThresholdAdmin(admin.ModelAdmin):
    list_display = ['school', 'tier1_amount', 'tier2_amount', 'tier3_amount']
    search_fields = ['school__name']


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ['vendor_name', 'school', 'amount', 'status', 'current_approver_role', 'created_at']
    list_filter = ['status', 'payment_type', 'school', 'created_at']
    search_fields = ['vendor_name', 'school__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PaymentApprovalInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Details', {
            'fields': ('school', 'payment_type', 'vendor_name', 'amount', 'currency', 'reason')
        }),
        ('Approvals Required', {
            'fields': ('requires_tier1_approval', 'requires_tier2_approval', 'requires_tier3_approval')
        }),
        ('Status', {
            'fields': ('status', 'current_approver_role')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['cancel_requests']
    
    def cancel_requests(self, request, queryset):
        queryset.filter(status='draft').update(status='cancelled')
        self.message_user(request, 'Draft requests cancelled.')


# ============================================================================
# 7. ACCESS CONTROLS ADMIN
# ============================================================================

@admin.register(RolePermissionGroup)
class RolePermissionGroupAdmin(admin.ModelAdmin):
    list_display = ['school', 'role', 'can_access_dashboard', 'can_approve_payments',
                   'can_view_audit_logs', 'can_manage_users']
    list_filter = ['role', 'school']
    search_fields = ['school__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Scope', {
            'fields': ('school', 'role')
        }),
        ('Module Access', {
            'fields': ('can_access_dashboard', 'can_view_students', 'can_edit_students',
                      'can_view_grades', 'can_edit_grades', 'can_view_attendance',
                      'can_edit_attendance', 'can_view_finances', 'can_edit_finances',
                      'can_approve_payments', 'can_view_audit_logs', 'can_export_reports',
                      'can_manage_users', 'can_view_ministry_dashboard')
        }),
        ('Data Scope', {
            'fields': ('can_see_all_schools', 'can_see_all_students', 'can_see_all_teachers',
                      'allowed_objects')
        }),
    )


@admin.register(UserAccessLog)
class UserAccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'was_allowed', 'accessed_at']
    list_filter = ['action', 'was_allowed', 'accessed_at', 'school']
    search_fields = ['user__email', 'resource_name']
    readonly_fields = ['accessed_at']
    date_hierarchy = 'accessed_at'
    
    fieldsets = (
        ('User', {
            'fields': ('user', 'school')
        }),
        ('Resource', {
            'fields': ('resource_type', 'resource_id', 'resource_name', 'action')
        }),
        ('Access Result', {
            'fields': ('was_allowed', 'denial_reason')
        }),
        ('Environment', {
            'fields': ('ip_address', 'user_agent', 'accessed_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False
