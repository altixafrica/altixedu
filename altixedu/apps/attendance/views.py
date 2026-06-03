from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import csv
from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Attendance.objects.select_related('student', 'recorded_by', 'school').order_by(
                '-date', 'student__last_name', 'student__first_name'
            )
        elif user.school:
            return Attendance.objects.filter(school=user.school).select_related(
                'student', 'recorded_by', 'school'
            ).order_by('-date', 'student__last_name', 'student__first_name')
        return Attendance.objects.none()

    def perform_create(self, serializer):
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export attendance records as CSV"""
        format_type = request.query_params.get('format', 'csv').lower()
        
        if format_type != 'csv':
            return Response(
                {'error': 'Only CSV format is currently supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Student ID', 'Student Name', 'Date', 'Status', 'Recorded By'
        ])
        
        for record in queryset:
            writer.writerow([
                record.student.admission_number if record.student else '',
                f"{record.student.first_name} {record.student.last_name}" if record.student else '',
                record.date,
                record.status,
                record.recorded_by.username if record.recorded_by else ''
            ])
        
        return response
