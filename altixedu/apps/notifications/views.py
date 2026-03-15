from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.db.models import Q, Avg
from apps.accounts.permissions import IsRoleOwnerOrAdmin
from .models import Message, StudentAIInsights, RoleSetting
from .serializers import (
    MessageSerializer,
    StudentAIInsightsSerializer,
    RoleSettingSerializer
)


class MessageViewSet(viewsets.ModelViewSet):
    """
    MessageViewSet provides endpoints for sending and managing messages.
    Custom actions: inbox, outbox, mark_as_read, unread_count
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Users can see messages where they are sender or receiver.
        Multi-tenancy: only show messages from their school.
        """
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            school=user.school
        ).order_by('-sent_at')

    def perform_create(self, serializer):
        """
        Override to set sender automatically and enforce multi-tenancy.
        """
        serializer.save(sender=self.request.user, school=self.request.user.school)

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        """
        Get all received messages (unread first).
        """
        messages = Message.objects.filter(
            receiver=request.user,
            school=request.user.school
        ).order_by('-read', '-sent_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def outbox(self, request):
        """
        Get all sent messages.
        """
        messages = Message.objects.filter(
            sender=request.user,
            school=request.user.school
        ).order_by('-sent_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific message as read.
        """
        message = self.get_object()
        
        # Only receiver can mark as read
        if message.receiver != request.user:
            return Response(
                {"detail": "Only receiver can mark message as read"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.read = True
        message.save()
        
        return Response(
            {"detail": "Message marked as read"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread messages.
        """
        count = Message.objects.filter(
            receiver=request.user,
            read=False,
            school=request.user.school
        ).count()
        
        return Response({"unread_count": count})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all unread messages as read for current user.
        """
        Message.objects.filter(
            receiver=request.user,
            read=False,
            school=request.user.school
        ).update(read=True)
        
        return Response(
            {"detail": "All messages marked as read"},
            status=status.HTTP_200_OK
        )


class StudentAIInsightsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing AI insights for students.
    School Admins can see all students' insights.
    Teachers can see their students' insights.
    Parents can see their children's insights.
    
    Actions:
    - at_risk: Get students with HIGH or CRITICAL risk
    - dashboard: Get risk summary and stats
    - calculate_risks: Trigger risk calculation (admin only)
    """
    serializer_class = StudentAIInsightsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Multi-tenancy: Filter based on user role and school.
        """
        user = self.request.user
        from apps.students.models import Student
        
        if user.role == 'superadmin':
            return StudentAIInsights.objects.all()
        
        if user.role == 'admin':
            # School Admin sees all students in their school
            return StudentAIInsights.objects.filter(school=user.school)
        
        if user.role == 'teacher':
            # Teacher sees only their students' insights
            from apps.academics.models import TeacherSubject
            classrooms = TeacherSubject.objects.filter(
                teacher=user
            ).values_list('classroom', flat=True).distinct()
            
            return StudentAIInsights.objects.filter(
                student__classroom__in=classrooms,
                school=user.school
            )
        
        if user.role == 'parent':
            # Parent sees their children's insights
            return StudentAIInsights.objects.filter(
                student__parents=user,
                school=user.school
            )
        
        return StudentAIInsights.objects.none()
    
    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """
        Get students with HIGH or CRITICAL risk.
        Useful for principal/teacher dashboard alerts.
        """
        queryset = self.get_queryset()
        
        # Filter by risk level (HIGH >= 0.5 or CRITICAL >= 0.7)
        risk_threshold = float(request.query_params.get('threshold', 0.5))
        at_risk_students = queryset.filter(overall_risk__gte=risk_threshold).order_by('-overall_risk')
        
        serializer = self.get_serializer(at_risk_students, many=True)
        return Response({
            'count': at_risk_students.count(),
            'threshold': risk_threshold,
            'students': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get AI insights dashboard with statistics.
        Shows: Total students, at-risk count, risk breakdown by level.
        """
        queryset = self.get_queryset()
        total = queryset.count()
        
        # Risk breakdown
        critical = queryset.filter(overall_risk__gte=0.7).count()
        high = queryset.filter(overall_risk__gte=0.5, overall_risk__lt=0.7).count()
        moderate = queryset.filter(overall_risk__gte=0.3, overall_risk__lt=0.5).count()
        low = queryset.filter(overall_risk__lt=0.3).count()
        
        # Aggregate metrics
        avg_attendance_risk = queryset.aggregate(
            avg=models.Avg('attendance_risk')
        )['avg'] or 0
        avg_performance_risk = queryset.aggregate(
            avg=models.Avg('performance_risk')
        )['avg'] or 0
        
        # Top flagged subjects
        all_flagged = []
        for insight in queryset.filter(flagged_subjects__gt=[]):
            all_flagged.extend(insight.flagged_subjects)
        
        from collections import Counter
        top_subjects = Counter(all_flagged).most_common(5)
        
        return Response({
            'total_students': total,
            'risk_breakdown': {
                'critical': critical,
                'high': high,
                'moderate': moderate,
                'low': low
            },
            'average_risks': {
                'attendance_risk': round(avg_attendance_risk, 2),
                'performance_risk': round(avg_performance_risk, 2)
            },
            'top_flagged_subjects': [
                {'subject': subject, 'count': count}
                for subject, count in top_subjects
            ]
        })
    
    @action(detail=False, methods=['post'])
    def calculate_risks(self, request):
        """
        Trigger AI risk calculation for all students.
        Only admins can trigger this.
        """
        user = request.user
        if user.role not in ['superadmin', 'admin']:
            return Response(
                {'detail': 'Only admins can trigger risk calculation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        count = 0
        errors = []
        
        for insight in queryset:
            try:
                insight.calculate_all_risks()
                count += 1
            except Exception as e:
                errors.append({
                    'student': str(insight.student),
                    'error': str(e)
                })
        
        return Response({
            'message': f'Risk calculation complete',
            'students_processed': count,
            'errors': errors if errors else None
        })
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get detailed summary for a single student with recommendations.
        """
        insight = self.get_object()
        
        # Ensure recommendations are fresh
        recommendations = insight.get_recommendations()
        
        serializer = self.get_serializer(insight)
        data = serializer.data
        data['recommendations'] = recommendations
        
        return Response(data)


class RoleSettingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing role-specific settings.
    Super Admin can manage all settings.
    School Admin can manage settings for their school.
    """
    serializer_class = RoleSettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsRoleOwnerOrAdmin]

    def get_queryset(self):
        """
        Multi-tenancy: Filter settings by user's role/school.
        """
        user = self.request.user
        
        if user.role == 'superadmin':
            return RoleSetting.objects.all()
        
        if user.role == 'admin':
            return RoleSetting.objects.filter(school=user.school)
        
        # Other roles can only see their own role's settings
        return RoleSetting.objects.filter(
            role=user.role,
            school=user.school
        )

    def perform_create(self, serializer):
        """
        Auto-set school for school admins.
        """
        if self.request.user.role == 'admin':
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """
        Get current user's role settings.
        """
        user = request.user
        settings = RoleSetting.objects.filter(
            role=user.role,
            school=user.school
        )
        
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)
