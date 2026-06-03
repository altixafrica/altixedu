from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import csv
from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Student.objects.select_related('classroom', 'school').order_by(
                'school__name', 'last_name', 'first_name'
            )
        elif user.school:
            return Student.objects.filter(school=user.school).select_related(
                'classroom', 'school'
            ).order_by('last_name', 'first_name')
        return Student.objects.none()

    def perform_create(self, serializer):
        # Auto-set school from user's school
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export students as CSV"""
        format_type = request.query_params.get('format', 'csv').lower()
        
        if format_type != 'csv':
            return Response(
                {'error': 'Only CSV format is currently supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Admission Number',
            'Email', 'Phone', 'Date of Birth', 'Gender', 'Status'
        ])
        
        for student in queryset:
            writer.writerow([
                student.id,
                student.first_name,
                student.last_name,
                student.admission_number,
                student.user.email if student.user else '',
                getattr(student, 'phone', ''),
                student.date_of_birth,
                student.gender,
                student.status
            ])
        
        return response
