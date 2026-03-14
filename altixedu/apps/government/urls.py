"""
URL Configuration for Government Features App
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MinistryDashboardViewSet,
    AuditLogViewSet,
    FinanceReportViewSet,
    ComplianceReportViewSet,
    OfflineSyncViewSet,
    PaymentApprovalThresholdViewSet,
    PaymentRequestViewSet,
    RolePermissionGroupViewSet,
    UserAccessLogViewSet,
)

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'dashboard/ministry', MinistryDashboardViewSet, basename='ministry-dashboard')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'reports/finance', FinanceReportViewSet, basename='finance-report')
router.register(r'reports/compliance', ComplianceReportViewSet, basename='compliance-report')
router.register(r'sync-queue', OfflineSyncViewSet, basename='offline-sync')
router.register(r'payments/thresholds', PaymentApprovalThresholdViewSet, basename='approval-threshold')
router.register(r'payments/requests', PaymentRequestViewSet, basename='payment-request')
router.register(r'permissions/roles', RolePermissionGroupViewSet, basename='role-permission')
router.register(r'access-logs', UserAccessLogViewSet, basename='access-log')

app_name = 'government'

urlpatterns = [
    path('', include(router.urls)),
]
