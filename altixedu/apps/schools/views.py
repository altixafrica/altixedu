from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count, Q
from apps.accounts.permissions import IsSchoolAdmin
from apps.accounts.models import User
from apps.students.models import Student
from apps.finance.models import StudentFee, Fee
from apps.notifications.models import StudentAIInsights, RoleSetting
from apps.academics.models import Classroom, Subject, TeacherSubject
from apps.notifications.serializers import (
    StudentAIInsightsSerializer,
    RoleSettingSerializer
)
from apps.schools.models import Ministry, School
from . import serializers
from .serializers import MinistrySerializer, SchoolDirectorySerializer
from .dashboard_payloads import build_school_admin_dashboard_payload


class MinistryViewSet(viewsets.ModelViewSet):
    """
    Superadmin can manage ministries.
    Ministry admins can only view their own ministry record.
    """
    serializer_class = MinistrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'superadmin':
            return Ministry.objects.all().order_by('country', 'state_or_province')

        if user.role == 'ministry_admin' and user.ministry_id:
            return Ministry.objects.filter(id=user.ministry_id)

        return Ministry.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.role != 'superadmin':
            return Response(
                {'error': 'Only superadmin can create ministries'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.role != 'superadmin':
            return Response(
                {'error': 'Only superadmin can update ministries'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'superadmin':
            return Response(
                {'error': 'Only superadmin can delete ministries'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)


class SchoolDirectoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Directory endpoint for school provisioning and oversight screens.
    """
    serializer_class = SchoolDirectorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = School.objects.select_related(
            'ministry',
            'subscription',
            'subscription__tier',
        )

        if user.role == 'superadmin':
            return queryset.order_by('name')

        if user.role == 'ministry_admin' and user.ministry_id:
            return queryset.filter(ministry_id=user.ministry_id).order_by('name')

        if user.school_id:
            return queryset.filter(id=user.school_id)

        return School.objects.none()


class SchoolViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for schools.
    Superadmin: Full access to all schools
    Ministry admin: Access to schools in their ministry
    School admin: Access to only their school
    """
    serializer_class = serializers.SchoolSerializer  # Will need to create this
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = School.objects.select_related('ministry', 'subscription', 'subscription__tier')
        
        if user.role == 'superadmin':
            return queryset.order_by('name')
        
        if user.role == 'ministry_admin' and user.ministry_id:
            return queryset.filter(ministry_id=user.ministry_id).order_by('name')
        
        if user.school_id:
            return queryset.filter(id=user.school_id)
        
        return School.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Only superadmin and ministry_admin can create schools"""
        if request.user.role not in ['superadmin', 'ministry_admin']:
            return Response(
                {'error': 'Only superadmin or ministry_admin can create schools'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If ministry_admin, auto-assign to their ministry
        if request.user.role == 'ministry_admin' and not request.data.get('ministry'):
            request.data['ministry'] = request.user.ministry_id
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Only superadmin can update all schools; others can only update their own"""
        school = self.get_object()
        
        if request.user.role == 'superadmin':
            return super().update(request, *args, **kwargs)
        
        if request.user.role == 'ministry_admin' and school.ministry_id == request.user.ministry_id:
            return super().update(request, *args, **kwargs)
        
        if request.user.school_id == school.id:
            return super().update(request, *args, **kwargs)
        
        return Response(
            {'error': 'You do not have permission to update this school'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def destroy(self, request, *args, **kwargs):
        """Only superadmin can delete schools"""
        if request.user.role != 'superadmin':
            return Response(
                {'error': 'Only superadmin can delete schools'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)


class SchoolAdminDashboardView(APIView):
    """
    School Admin dashboard showing all school data, financial summary, alerts, and settings.
    """
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        user = request.user
        school = user.school
        
        if not school:
            return Response(
                {"detail": "School Admin must be linked to a school"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(build_school_admin_dashboard_payload(user), status=status.HTTP_200_OK)
