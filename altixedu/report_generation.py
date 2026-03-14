"""
Attendance Report Generation
Generate PDF and CSV reports for attendance data
"""

import csv
import io
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from apps.attendance.models import Attendance
from apps.students.models import Student
from apps.academics.models import Classroom
import logging

logger = logging.getLogger(__name__)


class AttendanceReportGenerator:
    """Generate attendance reports in PDF and CSV formats"""
    
    def __init__(self, school=None, classroom=None, student=None, start_date=None, end_date=None):
        """
        Initialize report generator.
        
        Args:
            school: School instance (optional)
            classroom: Classroom instance (optional)
            student: Student instance (optional)
            start_date: Start date for attendance (datetime.date)
            end_date: End date for attendance (datetime.date)
        """
        self.school = school
        self.classroom = classroom
        self.student = student
        self.start_date = start_date or datetime.now().date() - timedelta(days=30)
        self.end_date = end_date or datetime.now().date()
    
    def get_attendance_data(self):
        """
        Retrieve attendance data based on filters.
        
        Returns:
            queryset of Attendance records
        """
        queryset = Attendance.objects.all()
        
        # Filter by date range
        queryset = queryset.filter(
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        # Filter by classroom (which implicitly filters students)
        if self.classroom:
            students = Student.objects.filter(classroom=self.classroom)
            queryset = queryset.filter(student__in=students)
        
        # Filter by specific student
        elif self.student:
            queryset = queryset.filter(student=self.student)
        
        # Filter by school
        if self.school:
            queryset = queryset.filter(student__school=self.school)
        
        return queryset.select_related('student', 'student__classroom').order_by(
            'student__classroom', 'student__admission_number', 'date'
        )
    
    def generate_csv(self):
        """
        Generate CSV report.
        
        Returns:
            CSV content as string
        """
        attendance_data = self.get_attendance_data()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Date',
            'Student Name',
            'Admission Number',
            'Classroom',
            'Status',
            'Remarks'
        ])
        
        # Data rows
        for record in attendance_data:
            writer.writerow([
                record.date.strftime('%Y-%m-%d'),
                f"{record.student.first_name} {record.student.last_name}",
                record.student.admission_number,
                str(record.student.classroom) if record.student.classroom else 'N/A',
                record.status.upper(),
                record.remarks or ''
            ])
        
        return output.getvalue()
    
    def generate_csv_summary(self):
        """
        Generate CSV summary report (attendance per student).
        
        Returns:
            CSV content as string
        """
        attendance_data = self.get_attendance_data()
        
        # Calculate attendance stats per student
        student_stats = {}
        
        for record in attendance_data:
            student_id = record.student.id
            
            if student_id not in student_stats:
                student_stats[student_id] = {
                    'student': record.student,
                    'total': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'excused': 0,
                }
            
            student_stats[student_id]['total'] += 1
            
            status = record.status.lower()
            if status == 'present':
                student_stats[student_id]['present'] += 1
            elif status == 'absent':
                student_stats[student_id]['absent'] += 1
            elif status == 'late':
                student_stats[student_id]['late'] += 1
            elif status == 'excused':
                student_stats[student_id]['excused'] += 1
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Student Name',
            'Admission Number',
            'Classroom',
            'Total Days',
            'Present',
            'Absent',
            'Late',
            'Excused',
            'Attendance %'
        ])
        
        # Data rows
        for student_id in sorted(student_stats.keys()):
            stats = student_stats[student_id]
            student = stats['student']
            
            attendance_pct = 0
            if stats['total'] > 0:
                attendance_pct = (stats['present'] / stats['total']) * 100
            
            writer.writerow([
                f"{student.first_name} {student.last_name}",
                student.admission_number,
                str(student.classroom) if student.classroom else 'N/A',
                stats['total'],
                stats['present'],
                stats['absent'],
                stats['late'],
                stats['excused'],
                f"{attendance_pct:.1f}%"
            ])
        
        return output.getvalue()
    
    def generate_pdf(self, filename="attendance_report.pdf"):
        """
        Generate PDF report.
        
        Returns:
            HttpResponse with PDF file
        """
        attendance_data = list(self.get_attendance_data())
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1  # Center
        )
        
        # Title
        elements.append(Paragraph("Attendance Report", title_style))
        
        # Report metadata
        metadata = f"Report Period: {self.start_date} to {self.end_date}"
        if self.classroom:
            metadata += f" | Classroom: {self.classroom.name}"
        elif self.student:
            metadata += f" | Student: {self.student.first_name} {self.student.last_name}"
        
        elements.append(Paragraph(metadata, styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Prepare table data
        table_data = [
            ['Date', 'Student Name', 'Admission No.', 'Classroom', 'Status', 'Remarks']
        ]
        
        for record in attendance_data:
            table_data.append([
                record.date.strftime('%Y-%m-%d'),
                f"{record.student.first_name} {record.student.last_name}",
                record.student.admission_number,
                str(record.student.classroom) if record.student.classroom else 'N/A',
                record.status.upper(),
                record.remarks or ''
            ])
        
        # Create table
        if len(table_data) > 1:
            table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1*inch, 0.8*inch, 1.5*inch])
            
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("No attendance data found for the given criteria.", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return as response
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def generate_pdf_summary(self, filename="attendance_summary.pdf"):
        """
        Generate PDF summary report (attendance per student).
        
        Returns:
            HttpResponse with PDF file
        """
        attendance_data = list(self.get_attendance_data())
        
        # Calculate attendance stats
        student_stats = {}
        for record in attendance_data:
            student_id = record.student.id
            
            if student_id not in student_stats:
                student_stats[student_id] = {
                    'student': record.student,
                    'total': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'excused': 0,
                }
            
            student_stats[student_id]['total'] += 1
            
            status = record.status.lower()
            if status == 'present':
                student_stats[student_id]['present'] += 1
            elif status == 'absent':
                student_stats[student_id]['absent'] += 1
            elif status == 'late':
                student_stats[student_id]['late'] += 1
            elif status == 'excused':
                student_stats[student_id]['excused'] += 1
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1
        )
        
        # Title
        elements.append(Paragraph("Attendance Summary Report", title_style))
        
        # Report metadata
        metadata = f"Report Period: {self.start_date} to {self.end_date}"
        elements.append(Paragraph(metadata, styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Prepare table
        table_data = [
            ['Student Name', 'Admission No.', 'Total Days', 'Present', 'Absent', 'Late', 'Excused', 'Attendance %']
        ]
        
        for student_id in sorted(student_stats.keys()):
            stats = student_stats[student_id]
            student = stats['student']
            
            attendance_pct = 0
            if stats['total'] > 0:
                attendance_pct = (stats['present'] / stats['total']) * 100
            
            table_data.append([
                f"{student.first_name} {student.last_name}",
                student.admission_number,
                str(stats['total']),
                str(stats['present']),
                str(stats['absent']),
                str(stats['late']),
                str(stats['excused']),
                f"{attendance_pct:.1f}%"
            ])
        
        # Create table
        if len(table_data) > 1:
            table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
            
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("No attendance data found.", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return as response
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
