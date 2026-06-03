from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import csv
from apps.teachers.models import Teacher
from apps.teachers.serializers import TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing teachers.
    
    list: Get all teachers for the current school
    retrieve: Get a specific teacher
    create: Create a new teacher
    update: Update teacher information
    destroy: Delete a teacher
    export: Export teachers as CSV
    """
    
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter teachers by current user's school"""
        user = self.request.user
        if hasattr(user, 'school'):
            return Teacher.objects.filter(school=user.school)
        return Teacher.objects.none()
    
    def perform_create(self, serializer):
        """Set school from user's school when creating"""
        user = self.request.user
        if hasattr(user, 'school'):
            serializer.save(school=user.school)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active teachers"""
        teachers = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export teachers as CSV"""
        format_type = request.query_params.get('format', 'csv').lower()
        
        if format_type != 'csv':
            return Response(
                {'error': 'Only CSV format is currently supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="staff.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Email', 'Phone',
            'Subject', 'Employment Status', 'Status'
        ])
        
        for teacher in queryset:
            writer.writerow([
                teacher.id,
                teacher.user.first_name if teacher.user else '',
                teacher.user.last_name if teacher.user else '',
                teacher.user.email if teacher.user else '',
                getattr(teacher, 'phone', ''),
                getattr(teacher, 'subject', ''),
                teacher.employment_status,
                teacher.status
            ])
        
        return response
