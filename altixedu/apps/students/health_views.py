"""
Views for Health and Medical Records
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.students.health_models import (
    StudentHealthRecord,
    StudentEmergencyContact,
    HealthMetric
)
from apps.students.health_serializers import (
    StudentHealthRecordSerializer,
    StudentEmergencyContactSerializer,
    HealthMetricSerializer
)
from apps.accounts.permissions import IsSchoolAdmin, IsTeacher
from altixedu.audit import log_action


class StudentHealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student health records.
    Only admins and teachers can view/edit health records.
    """
    serializer_class = StudentHealthRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter health records by user's school"""
        user = self.request.user
        
        if user.role == 'superadmin':
            return StudentHealthRecord.objects.all()
        elif user.role in ['admin', 'teacher']:
            return StudentHealthRecord.objects.filter(student__school=user.school)
        else:
            # Students/parents can only view their own/their child's health record
            if user.role == 'student':
                return StudentHealthRecord.objects.filter(student__user=user)
            elif user.role == 'parent':
                return StudentHealthRecord.objects.filter(student__parents=user)
            return StudentHealthRecord.objects.none()
    
    def get_permissions(self):
        """Only admins/teachers can create/edit health records"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Log health record creation"""
        instance = serializer.save()
        log_action(
            user=self.request.user,
            action_type='health_record_create',
            action_description=f'Health record created for {instance.student}',
            content_type='StudentHealthRecord',
            object_id=instance.id,
            object_name=f'Health Record - {instance.student}',
            request=self.request
        )
    
    def perform_update(self, serializer):
        """Log health record updates"""
        before = StudentHealthRecordSerializer(self.get_object()).data
        instance = serializer.save()
        after = StudentHealthRecordSerializer(instance).data
        
        log_action(
            user=self.request.user,
            action_type='health_record_update',
            action_description=f'Health record updated for {instance.student}',
            content_type='StudentHealthRecord',
            object_id=instance.id,
            object_name=f'Health Record - {instance.student}',
            before_value=before,
            after_value=after,
            request=self.request
        )


class StudentEmergencyContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student emergency contacts.
    """
    serializer_class = StudentEmergencyContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user's school and student"""
        user = self.request.user
        student_id = self.request.query_params.get('student_id')
        
        queryset = StudentEmergencyContact.objects.all()
        
        if user.role == 'superadmin':
            return queryset
        elif user.role in ['admin', 'teacher']:
            queryset = queryset.filter(student__school=user.school)
        elif user.role == 'student':
            queryset = queryset.filter(student__user=user)
        elif user.role == 'parent':
            queryset = queryset.filter(student__parents=user)
        else:
            queryset = StudentEmergencyContact.objects.none()
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset
    
    def get_permissions(self):
        """Only admins can create/edit emergency contacts"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Log emergency contact creation"""
        instance = serializer.save()
        log_action(
            user=self.request.user,
            action_type='emergency_contact_create',
            action_description=f'Emergency contact created: {instance.name}',
            content_type='StudentEmergencyContact',
            object_id=instance.id,
            object_name=instance.name,
            request=self.request
        )


class HealthMetricViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking student health metrics over time.
    Teachers and admins can record metrics.
    """
    serializer_class = HealthMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user's school"""
        user = self.request.user
        student_id = self.request.query_params.get('student_id')
        
        queryset = HealthMetric.objects.all()
        
        if user.role == 'superadmin':
            return queryset
        elif user.role in ['admin', 'teacher']:
            queryset = queryset.filter(student__school=user.school)
        elif user.role == 'student':
            queryset = queryset.filter(student__user=user)
        elif user.role == 'parent':
            queryset = queryset.filter(student__parents=user)
        else:
            queryset = HealthMetric.objects.none()
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset.order_by('-recorded_date')
    
    def get_permissions(self):
        """Only admins/teachers can create metrics"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Default recorded_by to current user"""
        serializer.save(recorded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_metric_type(self, request):
        """Get metrics grouped by type"""
        student_id = request.query_params.get('student_id')
        metric_type = request.query_params.get('type')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(student_id=student_id)
        
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
