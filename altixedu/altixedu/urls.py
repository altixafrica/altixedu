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
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.students.views import StudentViewSet
from apps.academics.views import (
    ClassroomViewSet,
    SubjectViewSet,
    TeacherSubjectViewSet,
    ExamViewSet,
    ExamResultViewSet
)
from apps.accounts.views import (
    UserViewSet, 
    ParentDashboardView,
    BursarDashboardView,
    LoginView,
    LogoutView,
    CurrentUserView,
    CreateMinistryAdminView,
    PasswordResetView,
    MinistryAdminLoginView,
    SchoolSetupView
)
from apps.schools.views import SchoolAdminDashboardView
from apps.attendance.views import AttendanceViewSet
from apps.finance.views import FeeViewSet, StudentFeeViewSet
from apps.notifications.views import (
    MessageViewSet,
    StudentAIInsightsViewSet,
    RoleSettingViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')
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
router.register(r'fees', FeeViewSet, basename='fees')
router.register(r'student-fees', StudentFeeViewSet, basename='student-fees')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'ai-insights', StudentAIInsightsViewSet, basename='ai-insights')
router.register(r'role-settings', RoleSettingViewSet, basename='role-settings')

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
    path('api/dashboard/schooladmin/', SchoolAdminDashboardView.as_view(), name='schooladmin-dashboard'),
    path('api/dashboard/bursar/', BursarDashboardView.as_view(), name='bursar-dashboard'),
    # Feature modules
    path('api/billing/', include('apps.billing.urls')),  # ⭐ Billing Features
    path('api/government/', include('apps.government.urls')),  # ⭐ Government Features
]
