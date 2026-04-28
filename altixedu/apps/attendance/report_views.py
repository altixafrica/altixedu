"""
Views for CSV Import and Attendance Report Generation
"""

import csv

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from datetime import datetime

from apps.accounts.models import User
from apps.accounts.permissions import IsSchoolAdmin
from apps.accounts.role_models import ParentStudentLink, StudentClassroomAssignment
from apps.academics.models import Classroom
from apps.students.models import Student
from bulk_import import BulkUserImporter, BulkUserImportError, get_csv_template
from report_generation import AttendanceReportGenerator
from audit import log_action


class BulkImportViewSet(viewsets.ViewSet):
    """
    ViewSet for bulk importing users from CSV.
    """
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    
    @action(detail=False, methods=['post'])
    def import_users(self, request):
        """
        Import users from CSV file.
        
        Request format (multipart/form-data):
        - file: CSV file with columns: username,email,password,first_name,last_name,role,school_id
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'CSV file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Only CSV files are accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Read file content
            csv_content = csv_file.read()
            
            # Create importer
            importer = BulkUserImporter(
                school=request.user.school,
                created_by=request.user
            )
            
            # Perform import
            results = importer.import_from_csv_content(csv_content)
            
            # Log the bulk import action
            log_action(
                user=request.user,
                action_type='bulk_user_import',
                action_description=f'Bulk imported {len(results["successful"])} users from CSV',
                content_type='User',
                object_id=0,
                object_name='Bulk Import',
                request=request
            )
            
            return Response(results, status=status.HTTP_200_OK)
        
        except BulkUserImportError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Import failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """Download CSV template for bulk import"""
        template = get_csv_template()
        
        response = HttpResponse(template, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_import_template.csv"'
        
        return response

    @action(detail=False, methods=['get'])
    def export_users(self, request):
        """Export school users as CSV."""
        rows = User.objects.filter(school=request.user.school).order_by('role', 'last_name', 'first_name')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="school_users.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'is_active', 'school_id'
        ])
        for user in rows:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user.role,
                user.phone or '',
                'true' if user.is_active else 'false',
                user.school_id or '',
            ])

        return response

    @action(detail=False, methods=['get'])
    def export_parent_links(self, request):
        """Export parent-student links as CSV."""
        rows = ParentStudentLink.objects.filter(
            student__school=request.user.school
        ).select_related('parent', 'student').order_by('student__last_name', 'student__first_name')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="parent_student_links.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'id', 'parent_id', 'parent_name', 'student_id', 'student_name',
            'relationship', 'is_primary', 'is_active'
        ])
        for row in rows:
            writer.writerow([
                row.id,
                row.parent_id,
                row.parent.get_full_name(),
                row.student_id,
                str(row.student),
                row.relationship,
                'true' if row.is_primary else 'false',
                'true' if row.is_active else 'false',
            ])

        return response

    @action(detail=False, methods=['get'])
    def export_classroom_assignments(self, request):
        """Export classroom assignments as CSV."""
        rows = StudentClassroomAssignment.objects.filter(
            student__school=request.user.school
        ).select_related('student', 'classroom').order_by('academic_year', 'classroom__name', 'roll_number')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="classroom_assignments.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'id', 'student_id', 'student_name', 'classroom_id', 'classroom_name',
            'academic_year', 'roll_number', 'is_active', 'assigned_date'
        ])
        for row in rows:
            writer.writerow([
                row.id,
                row.student_id,
                str(row.student),
                row.classroom_id,
                row.classroom.name,
                row.academic_year,
                row.roll_number,
                'true' if row.is_active else 'false',
                row.assigned_date,
            ])

        return response


class AttendanceReportViewSet(viewsets.ViewSet):
    """
    ViewSet for generating attendance reports in various formats.
    """
    permission_classes = [IsAuthenticated]
    
    def _get_report_generator(self, request):
        """Create report generator with filters from request"""
        classroom_id = request.query_params.get('classroom_id')
        student_id = request.query_params.get('student_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parse dates
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                start_date = None
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                end_date = None
        
        # Get classroom or student if specified
        classroom = None
        student = None
        
        if classroom_id:
            try:
                classroom = Classroom.objects.get(id=classroom_id, school=request.user.school)
            except Classroom.DoesNotExist:
                classroom = None
        
        if student_id:
            try:
                student = Student.objects.get(id=student_id, school=request.user.school)
            except Student.DoesNotExist:
                student = None
        
        return AttendanceReportGenerator(
            school=request.user.school,
            classroom=classroom,
            student=student,
            start_date=start_date,
            end_date=end_date
        )
    
    @action(detail=False, methods=['get'])
    def pdf(self, request):
        """
        Generate attendance report as PDF.
        
        Query parameters:
        - classroom_id: (optional) Filter by classroom
        - student_id: (optional) Filter by student
        - start_date: (optional) YYYY-MM-DD
        - end_date: (optional) YYYY-MM-DD
        """
        try:
            generator = self._get_report_generator(request)
            return generator.generate_pdf()
        except Exception as e:
            return Response(
                {'error': f'PDF generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def csv(self, request):
        """
        Generate attendance report as CSV.
        
        Query parameters:
        - classroom_id: (optional) Filter by classroom
        - student_id: (optional) Filter by student
        - start_date: (optional) YYYY-MM-DD
        - end_date: (optional) YYYY-MM-DD
        """
        try:
            generator = self._get_report_generator(request)
            csv_content = generator.generate_csv()
            
            response = HttpResponse(csv_content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
            
            return response
        except Exception as e:
            return Response(
                {'error': f'CSV generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def pdf_summary(self, request):
        """
        Generate attendance summary report (per student) as PDF.
        
        Query parameters:
        - classroom_id: (optional) Filter by classroom
        - start_date: (optional) YYYY-MM-DD
        - end_date: (optional) YYYY-MM-DD
        """
        try:
            generator = self._get_report_generator(request)
            return generator.generate_pdf_summary()
        except Exception as e:
            return Response(
                {'error': f'PDF summary generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def csv_summary(self, request):
        """
        Generate attendance summary report (per student) as CSV.
        
        Query parameters:
        - classroom_id: (optional) Filter by classroom
        - start_date: (optional) YYYY-MM-DD
        - end_date: (optional) YYYY-MM-DD
        """
        try:
            generator = self._get_report_generator(request)
            csv_content = generator.generate_csv_summary()
            
            response = HttpResponse(csv_content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance_summary.csv"'
            
            return response
        except Exception as e:
            return Response(
                {'error': f'CSV summary generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
