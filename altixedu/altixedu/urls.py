"""
URL configuration for altixedu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.students.views import StudentViewSet
from apps.teachers.views import TeacherViewSet
from apps.bursars.views import BursarViewSet
from apps.academics.views import (
    ClassroomViewSet,
    SubjectViewSet,
    TeacherSubjectViewSet,
    ExamViewSet,
    ExamResultViewSet,
    AcademicYearViewSet,
    TermViewSet
)
from apps.accounts.views import (
    UserViewSet, 
    ParentDashboardView,
    BursarDashboardView,
    StudentDashboardView,
    TeacherDashboardView,
    LoginView,
    LogoutView,
    CurrentUserView,
    CreateMinistryAdminView,
    PasswordResetView,
    MinistryAdminLoginView,
    SchoolSetupView
)
from apps.schools.views import SchoolAdminDashboardView, MinistryViewSet, SchoolViewSet, SchoolDirectoryViewSet
from apps.attendance.views import AttendanceViewSet
from apps.attendance.report_views import AttendanceReportViewSet, BulkImportViewSet
from apps.finance.views import FeeViewSet, StudentFeeViewSet
from apps.finance.payment_views import PaymentViewSet
from apps.notifications.views import (
    MessageViewSet,
    SchoolSettingViewSet,
    StudentAIInsightsViewSet,
    RoleSettingViewSet,
    NotificationPreferenceViewSet
)
from apps.students.health_views import (
    HealthMetricViewSet,
    StudentEmergencyContactViewSet,
    StudentHealthRecordViewSet,
)
from apps.accounts.role_views import (
    CustomRoleViewSet,
    ParentStudentLinkViewSet,
    RoleUserAssignmentViewSet,
    StudentClassroomAssignmentViewSet,
)
from apps.accounts.admin_management import (
    UserManagementViewSet,
    StudentManagementViewSet,
    ParentManagementViewSet,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')
router.register(r'teachers', TeacherViewSet, basename='teachers')
router.register(r'bursars', BursarViewSet, basename='bursars')
router.register(r'schools', SchoolViewSet, basename='schools')
router.register(r'schools-directory', SchoolDirectoryViewSet, basename='schools-directory')
router.register(r'ministries', MinistryViewSet, basename='ministries')
router.register(r'classrooms', ClassroomViewSet, basename='classrooms')
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(
    r'teacher-subjects',
    TeacherSubjectViewSet,
    basename='teacher-subjects'
)
router.register(r'users', UserViewSet, basename='users')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'exams', ExamViewSet, basename='exams')
router.register(r'exam-results', ExamResultViewSet, basename='exam-results')
router.register(r'academic-years', AcademicYearViewSet, basename='academic-years')
router.register(r'terms', TermViewSet, basename='terms')
router.register(r'fees', FeeViewSet, basename='fees')
router.register(r'student-fees', StudentFeeViewSet, basename='student-fees')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preferences')
router.register(r'ai-insights', StudentAIInsightsViewSet, basename='ai-insights')
router.register(r'role-settings', RoleSettingViewSet, basename='role-settings')
router.register(r'school-settings', SchoolSettingViewSet, basename='school-settings')
router.register(r'custom-roles', CustomRoleViewSet, basename='custom-roles')
router.register(r'role-assignments', RoleUserAssignmentViewSet, basename='role-assignments')
router.register(r'classroom-assignments', StudentClassroomAssignmentViewSet, basename='classroom-assignments')
router.register(r'parent-student-links', ParentStudentLinkViewSet, basename='parent-student-links')
router.register(r'user-management', UserManagementViewSet, basename='user-management')
router.register(r'student-management', StudentManagementViewSet, basename='student-management')
router.register(r'parent-management', ParentManagementViewSet, basename='parent-management')
router.register(r'bulk-import', BulkImportViewSet, basename='bulk-import')
router.register(r'attendance-reports', AttendanceReportViewSet, basename='attendance-reports')
router.register(r'health-records', StudentHealthRecordViewSet, basename='health-records')
router.register(r'emergency-contacts', StudentEmergencyContactViewSet, basename='emergency-contacts')
router.register(r'health-metrics', HealthMetricViewSet, basename='health-metrics')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication endpoints
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('api/auth/create-ministry-admin/', CreateMinistryAdminView.as_view(), name='create-ministry-admin'),
    path('api/auth/reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('api/auth/login/ministry/', MinistryAdminLoginView.as_view(), name='ministry-login'),
    path('api/schools/setup/', SchoolSetupView.as_view(), name='school-setup'),
    # API routes
    path('api/', include(router.urls)),
    # Dashboard endpoints
    path('api/dashboard/parent/', ParentDashboardView.as_view(), name='parent-dashboard'),
    path('api/dashboard/student/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('api/dashboard/teacher/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('api/dashboard/schooladmin/', SchoolAdminDashboardView.as_view(), name='schooladmin-dashboard'),
    path('api/dashboard/bursar/', BursarDashboardView.as_view(), name='bursar-dashboard'),
    path('api/platform/', include('apps.platform.urls')),
    # Feature modules
    path('api/billing/', include('apps.billing.urls')),  # ⭐ Billing Features
    path('api/government/', include('apps.government.urls')),  # ⭐ Government Features
    path('api/analytics/', include('apps.analytics.urls')),  # ⭐ Advanced Analytics
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
