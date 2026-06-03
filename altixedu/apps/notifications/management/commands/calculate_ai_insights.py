"""
Management command to calculate AI insights for all students.
Run regularly via Celery Beat or cron: python manage.py calculate_ai_insights
"""
from django.core.management.base import BaseCommand
from django.db.models import Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.students.models import Student
from apps.notifications.models import StudentAIInsights
from apps.attendance.models import Attendance
from apps.academics.models import ExamResult


class Command(BaseCommand):
    help = 'Calculate AI insights (risk scores) for all students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school',
            type=int,
            help='Calculate for specific school ID only'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )

    def handle(self, *args, **options):
        school_id = options.get('school')
        verbose = options.get('verbose', False)

        # Get all students or filter by school
        students = Student.objects.select_related('school', 'classroom')
        if school_id:
            students = students.filter(school_id=school_id)

        total_students = students.count()
        self.stdout.write(self.style.SUCCESS(f'Calculating AI insights for {total_students} students...'))

        processed = 0
        created = 0
        updated = 0

        for student in students:
            try:
                insight, was_created = StudentAIInsights.objects.get_or_create(
                    student=student,
                    school=student.school
                )

                # Calculate risks
                attendance_risk = self._calculate_attendance_risk(student)
                performance_risk = self._calculate_performance_risk(student)
                overall_risk = (attendance_risk + performance_risk) / 2

                # Update fields
                insight.attendance_risk = attendance_risk
                insight.performance_risk = performance_risk
                insight.overall_risk = overall_risk
                insight.low_attendance = attendance_risk > 0.5
                insight.low_performance = performance_risk > 0.5

                # Get attendance details
                thirty_days_ago = timezone.now() - timedelta(days=30)
                attendance_records = Attendance.objects.filter(
                    student=student,
                    date__gte=thirty_days_ago.date()
                )
                if attendance_records.exists():
                    total_records = attendance_records.count()
                    present_count = attendance_records.filter(status='present').count()
                    insight.attendance_percentage = (present_count / total_records * 100) if total_records > 0 else 0
                    insight.days_absent = total_records - present_count

                # Get performance details
                sixty_days_ago = timezone.now() - timedelta(days=60)
                exam_results = ExamResult.objects.filter(
                    student=student,
                    created_at__gte=sixty_days_ago
                )
                if exam_results.exists():
                    avg_grade = exam_results.aggregate(Avg('score'))['score__avg'] or 0
                    insight.average_grade = avg_grade
                    
                    # Get flagged subjects (below 70%)
                    flagged = exam_results.filter(score__lt=70).values_list('subject__name', flat=True).distinct()
                    insight.flagged_subjects = list(set(flagged))

                insight.save()

                if was_created:
                    created += 1
                else:
                    updated += 1

                processed += 1

                if verbose and processed % 10 == 0:
                    self.stdout.write(f'  Processed {processed}/{total_students}...')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {student}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n[SUCCESS] Complete!\n'
            f'  Processed: {processed}\n'
            f'  Created: {created}\n'
            f'  Updated: {updated}'
        ))

    def _calculate_attendance_risk(self, student):
        """Calculate attendance risk (0-1 scale). 1.0 = high risk, 0.0 = low risk"""
        threshold = 75  # Default attendance threshold
        
        # Get attendance for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        attendance_records = Attendance.objects.filter(
            student=student,
            date__gte=thirty_days_ago.date()
        )
        
        if not attendance_records.exists():
            return 0.3  # Unknown risk if no data
        
        total_records = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        attendance_pct = (present_count / total_records * 100) if total_records > 0 else 0
        
        # Risk calculation
        if attendance_pct >= threshold:
            return 0.0  # Low risk
        elif attendance_pct < 50:
            return 1.0  # High risk
        else:
            # Linear scale between 50-75%
            return (threshold - attendance_pct) / (threshold - 50)

    def _calculate_performance_risk(self, student):
        """Calculate performance risk (0-1 scale). 1.0 = high risk, 0.0 = low risk"""
        threshold = 70.0  # Default performance threshold
        
        # Get exam results for last 60 days
        sixty_days_ago = timezone.now() - timedelta(days=60)
        exam_results = ExamResult.objects.filter(
            student=student,
            created_at__gte=sixty_days_ago
        )
        
        if not exam_results.exists():
            return 0.3  # Moderate risk if no recent exam data
        
        avg_grade = exam_results.aggregate(Avg('score'))['score__avg'] or 0
        
        # Risk calculation
        if avg_grade >= threshold:
            return 0.0  # Low risk
        elif avg_grade < 50:
            return 1.0  # High risk
        else:
            # Linear scale between 50-70%
            return (threshold - avg_grade) / (threshold - 50)
