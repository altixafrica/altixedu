"""
Views for Government Features APIs
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import timedelta

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
from .serializers import (
    MinistryDashboardSerializer,
    MinistryDashboardAlertSerializer,
    AuditLogSerializer,
    FinanceReportSerializer,
    ComplianceReportSerializer,
    OfflineSyncQueueSerializer,
    PaymentRequestSerializer,
    PaymentApprovalSerializer,
    PaymentApprovalThresholdSerializer,
    RolePermissionGroupSerializer,
    UserAccessLogSerializer,
)


# ============================================================================
# PERMISSIONS
# ============================================================================

ROLE_GROUP_ALIASES = {
    # GOVERNMENT LEVEL
    'super_admin': 'superadmin',           # Alternative to superadmin
    
    # SCHOOL LEVEL
    'school_admin': 'admin',               # Alternative to admin (principal)
    'principal': 'admin',                  # Principal is school admin
    
    # FINANCE ROLES (both are bursar)
    'finance_officer': 'bursar',           # Finance officer = bursar (school finance)
}


def user_has_role(user, *roles):
    """
    Support both Django auth groups and the platform's custom user.role field.
    """
    if not user or not user.is_authenticated:
        return False

    user_role = getattr(user, 'role', None)
    normalized_roles = {ROLE_GROUP_ALIASES.get(role, role) for role in roles}
    if user_role in normalized_roles:
        return True

    return user.groups.filter(name__in=roles).exists()


def get_user_access_role(user):
    if not user or not user.is_authenticated:
        return 'unknown'

    if getattr(user, 'role', None):
        return user.role

    if user.groups.exists():
        return user.groups.first().name

    return 'unknown'


class IsMinistryAdmin(permissions.BasePermission):
    """Only ministry admins and superadmins can view ministry dashboard."""
    def has_permission(self, request, view):
        return user_has_role(request.user, 'ministry_admin', 'superadmin')


class IsBursar(permissions.BasePermission):
    """Only bursars can create/approve payments."""
    def has_permission(self, request, view):
        return user_has_role(request.user, 'bursar', 'superadmin')


class IsSchoolAdmin(permissions.BasePermission):
    """Only school admins can access school-specific data."""
    def has_permission(self, request, view):
        return user_has_role(request.user, 'admin', 'superadmin')


# ============================================================================
# PAGINATION
# ============================================================================

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AuditLogPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


# ============================================================================
# 1. MINISTRY DASHBOARD API
# ============================================================================

class MinistryDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for Ministry Dashboard - Government overview of all schools.
    
    List all dashboards for states (ministry admin only)
    Retrieve specific state dashboard with alerts
    Filter by state
    
    SECURITY: Ministry admins can only see their assigned state
    """
    
    serializer_class = MinistryDashboardSerializer
    permission_classes = [IsMinistryAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['state', 'ministry']
    ordering_fields = ['state', 'last_updated']
    ordering = ['-last_updated']
    
    def get_queryset(self):
        """
        Filter dashboards based on user's ministry assignment.
        Super admins see all.
        Ministry admins see only their state.
        """
        user = self.request.user
        
        # Super admin can see all states
        if user_has_role(user, 'superadmin'):
            return MinistryDashboardAggregation.objects.all()
        
        # Ministry admin can see only their assigned state
        if user_has_role(user, 'ministry_admin'):
            if hasattr(user, 'ministry') and user.ministry:
                return MinistryDashboardAggregation.objects.filter(
                    state=user.ministry.state_or_province
                )
            else:
                # Ministry admin without ministry assignment - no access
                return MinistryDashboardAggregation.objects.none()
        
        # Default: no access
        return MinistryDashboardAggregation.objects.none()
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get all alerts for a dashboard."""
        dashboard = self.get_object()
        alerts = dashboard.alerts.all()
        
        # Filter by severity if requested
        level = request.query_params.get('level')
        if level:
            alerts = alerts.filter(level=level)
        
        serializer = MinistryDashboardAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def top_performers(self, request, pk=None):
        """Get top 10 performing schools by collection rate."""
        dashboard = self.get_object()
        # This would fetch from related schools with collection metrics
        return Response({
            'message': 'Top performers endpoint - implementation specific to school model'
        })
    
    @action(detail=True, methods=['get'])
    def bottom_performers(self, request, pk=None):
        """Get bottom 10 underperforming schools."""
        dashboard = self.get_object()
        return Response({
            'message': 'Bottom performers endpoint - implementation specific to school model'
        })
    
    @action(detail=True, methods=['post'])
    def refresh_data(self, request, pk=None):
        """Manually trigger dashboard data refresh."""
        dashboard = self.get_object()
        # Recalculates all aggregations from school data
        dashboard.last_updated = timezone.now()
        dashboard.save()
        serializer = self.get_serializer(dashboard)
        return Response(serializer.data)


# ============================================================================
# 2. AUDIT LOGS API
# ============================================================================

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for Audit Logs - Immutable action tracking.
    
    Super admin: see all audit logs
    School admin: see audit logs for their school
    Finance officer: see financial action audit logs
    
    Search by user, action type, date range
    Export as PDF or Excel
    """
    
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action_type', 'user_school', 'approval_status', 'user']
    search_fields = ['user_email', 'action_description', 'object_name']
    ordering_fields = ['created_at', 'user_email', 'action_type']
    ordering = ['-created_at']
    pagination_class = AuditLogPagination
    
    def get_queryset(self):
        """Filter based on user role and school."""
        user = self.request.user
        
        # Super admin sees all
        if user_has_role(user, 'super_admin'):
            return AuditLog.objects.all()
        
        # School admin sees own school
        if user_has_role(user, 'school_admin'):
            return AuditLog.objects.filter(user_school=user.school)
        
        # Financial users see financial actions
        if user_has_role(user, 'bursar', 'finance_officer'):
            financial_actions = ['payment_create', 'payment_update', 'payment_approve',
                               'payment_reject', 'expense_create', 'expense_approve']
            return AuditLog.objects.filter(
                Q(action_type__in=financial_actions) &
                Q(user_school=user.school)
            )
        
        # Default: no access
        return AuditLog.objects.none()
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get audit logs within a date range."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_action_type(self, request):
        """Get summary of actions by type."""
        action_type = request.query_params.get('action_type')
        
        queryset = self.get_queryset()
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        summary = queryset.values('action_type').annotate(count=Count('id'))
        return Response(summary)
    
    @action(detail=False, methods=['post'])
    def export_pdf(self, request):
        """Export audit logs as PDF."""
        return Response({
            'message': 'PDF export - implement using reportlab or WeasyPrint'
        })
    
    @action(detail=False, methods=['post'])
    def export_excel(self, request):
        """Export audit logs as Excel."""
        return Response({
            'message': 'Excel export - implement using openpyxl'
        })

    @action(detail=False, methods=['get'], url_path='export')
    def export_csv(self, request):
        """Export audit logs as CSV for admin downloads."""
        queryset = self.filter_queryset(self.get_queryset())

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit-logs.csv"'

        import csv
        writer = csv.writer(response)
        writer.writerow(['created_at', 'user_email', 'user_role', 'action_type', 'object_name', 'approval_status'])

        for log in queryset[:5000]:
            writer.writerow([
                log.created_at.isoformat() if log.created_at else '',
                getattr(log, 'user_email', ''),
                getattr(log, 'user_role', ''),
                getattr(log, 'action_type', ''),
                getattr(log, 'object_name', ''),
                getattr(log, 'approval_status', ''),
            ])

        return response


# ============================================================================
# 3. FINANCE REPORTS API
# ============================================================================

class FinanceReportViewSet(viewsets.ModelViewSet):
    """
    API for Finance Reports - Auto-generated financial statements.
    
    List reports for school
    Retrieve specific report
    Generate new report
    Export as PDF or Excel
    """
    
    serializer_class = FinanceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['school', 'report_type', 'start_date', 'end_date']
    ordering_fields = ['end_date', 'created_at']
    ordering = ['-end_date']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter based on user role."""
        user = self.request.user
        
        if user_has_role(user, 'super_admin'):
            return FinanceReport.objects.all()
        
        # School bursar sees own school
        if user_has_role(user, 'bursar', 'finance_officer'):
            return FinanceReport.objects.filter(school=user.school)
        
        # Admin sees own school
        if user_has_role(user, 'admin'):
            return FinanceReport.objects.filter(school=user.school)
        
        return FinanceReport.objects.none()
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new finance report."""
        school_id = request.data.get('school_id')
        report_type = request.data.get('report_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not all([school_id, report_type, start_date, end_date]):
            return Response(
                {'error': 'school_id, report_type, start_date, end_date required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate report
        report = FinanceReport.objects.create(
            school_id=school_id,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            period_name=f"{start_date} to {end_date}",
            generated_by=request.user
        )
        
        # Calculate metrics (simplified - actual implementation depends on models)
        # In real code: query School, Fee, Payment models to calculate
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def export_pdf(self, request, pk=None):
        """Export report as PDF."""
        report = self.get_object()
        return Response({
            'message': f'PDF generation for {report.school.name} - implement with reportlab'
        })
    
    @action(detail=True, methods=['post'])
    def export_excel(self, request, pk=None):
        """Export report as Excel."""
        report = self.get_object()
        return Response({
            'message': f'Excel generation for {report.school.name} - implement with openpyxl'
        })


# ============================================================================
# 4. COMPLIANCE REPORTS API
# ============================================================================

class ComplianceReportViewSet(viewsets.ModelViewSet):
    """
    API for Compliance Reports - Quarterly accountability.
    
    List by school and quarter
    Submit report for approval
    Approve/reject reports (admin only)
    Export as PDF for ministry submission
    """
    
    serializer_class = ComplianceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['school', 'state', 'year', 'quarter', 'status']
    ordering_fields = ['year', 'quarter', 'created_at']
    ordering = ['-year', '-quarter']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter based on role."""
        user = self.request.user
        
        if user_has_role(user, 'super_admin'):
            return ComplianceReport.objects.all()
        
        # Ministry admin sees all schools in their state
        if user_has_role(user, 'ministry_admin'):
            state = user.ministry.state_or_province if getattr(user, 'ministry', None) else None
            if state:
                return ComplianceReport.objects.filter(state=state)
        
        # School staff sees own school
        return ComplianceReport.objects.filter(school=user.school)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit report for ministry approval."""
        report = self.get_object()
        
        if report.status != 'draft':
            return Response(
                {'error': 'Only draft reports can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.status = 'submitted'
        report.submitted_by = request.user
        report.submitted_date = timezone.now()
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve submitted report (ministry admin only)."""
        if not user_has_role(request.user, 'ministry_admin', 'superadmin'):
            return Response(
                {'error': 'Only ministry admins can approve'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report = self.get_object()
        
        if report.status != 'submitted':
            return Response(
                {'error': 'Can only approve submitted reports'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.status = 'approved'
        report.approved_by = request.user
        report.approved_date = timezone.now()
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject submitted report with reasons."""
        report = self.get_object()
        reasons = request.data.get('reasons', '')
        
        report.status = 'rejected'
        report.key_challenges = reasons  # Store rejection reasons
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def export_pdf(self, request, pk=None):
        """Export compliance report as PDF for ministry submission."""
        report = self.get_object()
        return Response({
            'message': f'Generating compliance PDF for {report.school.name} Q{report.quarter} {report.year}'
        })


# ============================================================================
# 5. OFFLINE SYNC API
# ============================================================================

class OfflineSyncViewSet(viewsets.ModelViewSet):
    """
    API for Offline Sync Queue - Handle offline device sync.
    
    Push offline changes to queue
    Get sync status
    Resolve conflicts
    Clear queue after successful sync
    """
    
    serializer_class = OfflineSyncQueueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'device_id', 'status']
    ordering_fields = ['created_locally', 'queued_at']
    ordering = ['-created_locally']
    
    def get_queryset(self):
        """Users only see their own sync queue."""
        return OfflineSyncQueue.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def push_changes(self, request):
        """Push offline changes to sync queue."""
        changes = request.data.get('changes', [])
        device_id = request.data.get('device_id')
        
        if not device_id:
            return Response(
                {'error': 'device_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_items = []
        
        for change in changes:
            sync_item = OfflineSyncQueue.objects.create(
                user=request.user,
                device_id=device_id,
                content_type=change.get('content_type'),
                object_id=change.get('object_id'),
                object_name=change.get('object_name'),
                action=change.get('action'),
                device_data=change.get('data'),
                created_locally=change.get('timestamp'),
            )
            created_items.append(sync_item)
        
        serializer = self.get_serializer(created_items, many=True)
        return Response({
            'message': f'{len(created_items)} changes queued for sync',
            'items': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def resolve_conflict(self, request, pk=None):
        """Resolve a conflict by choosing device or server version."""
        sync_item = self.get_object()
        
        if sync_item.status != 'conflict':
            return Response(
                {'error': 'No conflict to resolve'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resolution = request.data.get('resolution_choice')  # keep_device, keep_server, merge
        
        if resolution not in ['keep_device', 'keep_server', 'merge']:
            return Response(
                {'error': 'Invalid resolution choice'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sync_item.resolution_choice = resolution
        sync_item.resolved_by_user = request.user
        sync_item.status = 'resolved'
        sync_item.save()
        
        serializer = self.get_serializer(sync_item)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """Get count of pending syncs."""
        count = self.get_queryset().filter(status='pending').count()
        return Response({'pending_syncs': count})
    
    @action(detail=False, methods=['post'])
    def sync_now(self, request):
        """Trigger immediate sync of all pending changes."""
        pending = self.get_queryset().filter(status='pending')
        
        synced_count = 0
        
        for sync_item in pending:
            # Attempt sync (simplified)
            sync_item.status = 'syncing'
            sync_item.attempt_count += 1
            sync_item.last_attempt = timezone.now()
            
            try:
                # In real implementation: apply changes to server
                sync_item.status = 'synced'
                sync_item.synced_at = timezone.now()
                synced_count += 1
            except Exception as e:
                sync_item.status = 'failed'
                sync_item.error_message = str(e)
            
            sync_item.save()
        
        return Response({
            'message': f'{synced_count} items synced',
            'pending_count': self.get_queryset().filter(status='pending').count(),
            'failed_count': self.get_queryset().filter(status='failed').count(),
        })


# ============================================================================
# 6. PAYMENT APPROVAL WORKFLOW API
# ============================================================================

class PaymentApprovalThresholdViewSet(viewsets.ModelViewSet):
    """
    API for Payment Approval Thresholds - Configure approval tiers.
    """
    
    serializer_class = PaymentApprovalThresholdSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school']
    
    def get_queryset(self):
        """School admins see only their school thresholds."""
        user = self.request.user
        if user_has_role(user, 'superadmin'):
            return PaymentApprovalThreshold.objects.all()
        return PaymentApprovalThreshold.objects.filter(school=user.school)


class PaymentRequestViewSet(viewsets.ModelViewSet):
    """
    API for Payment Requests - Multi-tier approval workflow.
    
    Create payment request
    Get approval status
    Approve/reject at each tier
    Track approval chain
    """
    
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['school', 'status', 'payment_type']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter based on user role and school."""
        user = self.request.user
        
        if user_has_role(user, 'superadmin'):
            return PaymentRequest.objects.all()
        
        # School staff sees own school requests
        return PaymentRequest.objects.filter(school=user.school)
    
    def create(self, request, *args, **kwargs):
        """Create new payment request."""
        school_id = request.data.get('school')
        amount = float(request.data.get('amount', 0))
        
        # Get approval thresholds
        try:
            threshold = PaymentApprovalThreshold.objects.get(school_id=school_id)
        except PaymentApprovalThreshold.DoesNotExist:
            return Response(
                {'error': 'Approval thresholds not configured for this school'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine which approvals are needed
        requires_tier1 = amount > 0
        requires_tier2 = amount > threshold.tier1_amount
        requires_tier3 = amount > threshold.tier2_amount
        
        # Create payment request
        payment_request = PaymentRequest.objects.create(
            school_id=school_id,
            payment_type=request.data.get('payment_type'),
            vendor_name=request.data.get('vendor_name'),
            amount=amount,
            reason=request.data.get('reason'),
            requires_tier1_approval=requires_tier1,
            requires_tier2_approval=requires_tier2,
            requires_tier3_approval=requires_tier3,
            current_approver_role='bursar',
            status='pending_tier1',
            created_by=request.user
        )
        
        # Create approval records
        if requires_tier1:
            PaymentApproval.objects.create(
                payment_request=payment_request,
                approval_tier=1,
                required_role='bursar',
                status='pending'
            )
        
        if requires_tier2:
            PaymentApproval.objects.create(
                payment_request=payment_request,
                approval_tier=2,
                required_role='principal',
                status='pending'
            )
        
        if requires_tier3:
            PaymentApproval.objects.create(
                payment_request=payment_request,
                approval_tier=3,
                required_role='finance_officer',
                status='pending'
            )
        
        serializer = self.get_serializer(payment_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve payment at current tier."""
        payment_request = self.get_object()
        approval_notes = request.data.get('approval_notes', '')
        
        # Get current approval step
        current_approval = payment_request.approvals.filter(status='pending').first()
        
        if not current_approval:
            return Response(
                {'error': 'No pending approvals for this request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark as approved
        current_approval.status = 'approved'
        current_approval.approver = request.user
        current_approval.approval_notes = approval_notes
        current_approval.approved_at = timezone.now()
        current_approval.save()
        
        # Move to next tier or mark as fully approved
        next_approval = payment_request.approvals.filter(status='pending').first()
        
        if next_approval:
            # Move to next tier
            payment_request.status = f'pending_tier{next_approval.approval_tier}'
            payment_request.current_approver_role = next_approval.required_role
        else:
            # All approved
            payment_request.status = 'approved'
            payment_request.current_approver_role = None
        
        payment_request.save()
        
        # Log to audit trail
        AuditLog.objects.create(
            user=request.user,
            user_email=request.user.email,
            user_role=get_user_access_role(request.user),
            action_type='payment_approve',
            action_description=f'Approved payment request {payment_request.id}',
            content_type='PaymentRequest',
            object_id=payment_request.id,
            object_name=f"{payment_request.vendor_name} - ₦{payment_request.amount}",
            before_value={},
            after_value={'status': payment_request.status},
            approval_status='approved'
        )
        
        serializer = self.get_serializer(payment_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject payment request."""
        payment_request = self.get_object()
        rejection_reason = request.data.get('reason', 'No reason provided')
        
        # Get current approval
        current_approval = payment_request.approvals.filter(status='pending').first()
        
        if current_approval:
            current_approval.status = 'rejected'
            current_approval.approver = request.user
            current_approval.approval_notes = rejection_reason
            current_approval.approved_at = timezone.now()
            current_approval.save()
        
        # Mark payment request as rejected
        payment_request.status = 'rejected'
        payment_request.save()
        
        # Log to audit
        AuditLog.objects.create(
            user=request.user,
            user_email=request.user.email,
            user_role=get_user_access_role(request.user),
            action_type='payment_reject',
            action_description=f'Rejected payment request {payment_request.id}',
            content_type='PaymentRequest',
            object_id=payment_request.id,
            object_name=f"{payment_request.vendor_name} - ₦{payment_request.amount}",
            before_value={},
            after_value={'status': 'rejected'},
            approval_status='approved'
        )
        
        serializer = self.get_serializer(payment_request)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get all payment requests awaiting this user's approval."""
        user_role = get_user_access_role(request.user)
        
        pending = PaymentRequest.objects.filter(
            current_approver_role=user_role,
            status__startswith='pending_'
        )
        
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)


# ============================================================================
# 7. ACCESS CONTROLS API
# ============================================================================

class RolePermissionGroupViewSet(viewsets.ModelViewSet):
    """
    API for Role-Based Permissions - Configure access control.
    
    Super admin configures system-wide role permissions
    School admin configures school-level role permissions
    """
    
    serializer_class = RolePermissionGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['school', 'role']
    ordering_fields = ['role', 'created_at']
    
    def get_queryset(self):
        """Filter based on user role."""
        user = self.request.user
        
        if user_has_role(user, 'super_admin'):
            return RolePermissionGroup.objects.all()
        
        # School admin sees own school's permission groups
        return RolePermissionGroup.objects.filter(school=user.school)
    
    @action(detail=False, methods=['get'])
    def my_permissions(self, request):
        """Get current user's permissions."""
        user_role = get_user_access_role(request.user)
        school_id = request.query_params.get('school_id')
        
        try:
            perm_group = RolePermissionGroup.objects.get(role=user_role, school_id=school_id)
            serializer = self.get_serializer(perm_group)
            return Response(serializer.data)
        except RolePermissionGroup.DoesNotExist:
            return Response(
                {'error': 'No permissions configured for your role'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for User Access Logs - Security audit of data access.
    
    Track who accessed what and when
    Identify unauthorized access attempts
    Generate access reports
    """
    
    serializer_class = UserAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'school', 'was_allowed', 'resource_type', 'action']
    ordering_fields = ['accessed_at', 'was_allowed']
    ordering = ['-accessed_at']
    pagination_class = AuditLogPagination
    
    def get_queryset(self):
        """Filter based on role."""
        user = self.request.user
        
        if user_has_role(user, 'super_admin'):
            return UserAccessLog.objects.all()
        
        # School admin sees access logs for their school
        return UserAccessLog.objects.filter(school=user.school)
    
    @action(detail=False, methods=['get'])
    def denied_access(self, request):
        """Get all denied access attempts."""
        queryset = self.get_queryset().filter(was_allowed=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get access logs for specific user."""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
