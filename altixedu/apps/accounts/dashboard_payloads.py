from django.db.models import Count, F, Prefetch, Q, Sum
from datetime import timedelta
from django.utils import timezone

from apps.attendance.models import Attendance
from apps.finance.models import StudentFee
from apps.notifications.models import Message, RoleSetting, StudentAIInsights
from apps.students.models import Student


def build_bursar_dashboard_payload(user):
    school = user.school
    student_fees = StudentFee.objects.filter(fee__school=school).select_related('student', 'fee')

    total_due = student_fees.aggregate(Sum('fee__amount'))['fee__amount__sum'] or 0
    total_paid = student_fees.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_balance = total_due - total_paid

    fees_by_status = [
        {
            'status': 'paid',
            'count': student_fees.filter(amount_paid__gte=F('fee__amount')).count(),
            'total': student_fees.filter(amount_paid__gte=F('fee__amount')).aggregate(total=Sum('amount_paid'))['total'] or 0,
        },
        {
            'status': 'partial',
            'count': student_fees.filter(amount_paid__gt=0, amount_paid__lt=F('fee__amount')).count(),
            'total': student_fees.filter(amount_paid__gt=0, amount_paid__lt=F('fee__amount')).aggregate(total=Sum('amount_paid'))['total'] or 0,
        },
        {
            'status': 'unpaid',
            'count': student_fees.filter(amount_paid=0).count(),
            'total': student_fees.filter(amount_paid=0).aggregate(total=Sum('fee__amount'))['total'] or 0,
        },
    ]

    return {
        'school': {
            'id': school.id,
            'name': school.name,
        },
        'financial_summary': {
            'total_due': float(total_due),
            'total_paid': float(total_paid),
            'balance': float(total_balance),
            'collection_rate': (total_paid / total_due * 100) if total_due > 0 else 0,
        },
        'fees_by_status': fees_by_status,
        'total_students': Student.objects.filter(school=school).count(),
    }


def build_parent_dashboard_payload(user):
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    students = list(
        Student.objects.filter(parents=user)
        .select_related('classroom', 'school')
        .prefetch_related(
            Prefetch('fees', queryset=StudentFee.objects.select_related('fee')),
            Prefetch('ai_insights', queryset=StudentAIInsights.objects.order_by('-created_at')),
        )
        .order_by('first_name', 'last_name')
    )

    student_ids = [student.id for student in students]
    attendance_rows = Attendance.objects.filter(
        student_id__in=student_ids,
        date__gte=thirty_days_ago
    ).values('student_id').annotate(
        total_days=Count('id'),
        present_days=Count('id', filter=Q(status='present')),
        absent_days=Count('id', filter=Q(status='absent')),
        late_days=Count('id', filter=Q(status='late')),
    )
    attendance_map = {row['student_id']: row for row in attendance_rows}

    fees_data = []
    attendance_data = []
    ai_insights_data = []

    for student in students:
        student_name = f'{student.first_name} {student.last_name}'
        student_fees = list(student.fees.all())
        total_due = sum(fee.fee.amount for fee in student_fees)
        total_paid = sum(fee.amount_paid for fee in student_fees)
        balance = total_due - total_paid

        fees_data.append({
            'student_id': student.id,
            'student_name': student_name,
            'total_due': total_due,
            'amount_paid': total_paid,
            'balance': balance,
            'paid': balance <= 0,
        })

        attendance = attendance_map.get(student.id, {})
        total_days = attendance.get('total_days', 0) or 0
        present_days = attendance.get('present_days', 0) or 0
        absent_days = attendance.get('absent_days', 0) or 0
        late_days = attendance.get('late_days', 0) or 0
        attendance_data.append({
            'student_id': student.id,
            'student_name': student_name,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'attendance_percentage': (present_days / total_days * 100) if total_days > 0 else 0,
        })

        ai_insight = next(iter(student.ai_insights.all()), None)
        if ai_insight:
            ai_insights_data.append({
                'student_id': student.id,
                'student_name': student_name,
                'attendance_risk': ai_insight.attendance_risk,
                'performance_risk': ai_insight.performance_risk,
                'low_attendance': ai_insight.low_attendance,
                'low_performance': ai_insight.low_performance,
                'flagged_subjects': ai_insight.flagged_subjects,
            })

    settings = RoleSetting.objects.filter(role='parent', school=user.school)
    unread_messages = Message.objects.filter(receiver=user, read=False, school=user.school).count()

    return {
        'user': {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'role': user.role,
            'school': user.school.name if user.school else None,
        },
        'children': [
            {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'admission_number': student.admission_number,
                'classroom': student.classroom.name if student.classroom else None,
                'status': student.status,
                'gender': student.gender,
            }
            for student in students
        ],
        'fees': fees_data,
        'attendance': attendance_data,
        'ai_insights': ai_insights_data,
        'messages': {
            'unread_count': unread_messages,
        },
        'settings': {setting.key: setting.value for setting in settings},
    }


def build_student_dashboard_payload(user):
    from datetime import timedelta
    from django.utils import timezone
    from apps.academics.models import ExamResult, TeacherSubject

    student = Student.objects.filter(user=user).select_related('classroom', 'school').first()
    if not student:
        return None

    attendance_window = timezone.now().date() - timedelta(days=30)
    attendance_records = Attendance.objects.filter(student=student, date__gte=attendance_window).order_by('-date')
    exam_results = ExamResult.objects.filter(student=student).select_related('subject', 'exam').order_by('-created_at')[:12]
    insight = StudentAIInsights.objects.filter(student=student).first()
    settings = RoleSetting.objects.filter(role='student', school=student.school)
    unread_messages = Message.objects.filter(receiver=user, read=False, school=student.school).count()

    classroom_subjects = []
    if student.classroom_id:
        classroom_subjects = [
            {
                'id': assignment.subject.id,
                'name': assignment.subject.name,
                'code': assignment.subject.code,
            }
            for assignment in TeacherSubject.objects.filter(classroom_id=student.classroom_id).select_related('subject')
        ]

    total_attendance = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    late_days = attendance_records.filter(status='late').count()
    attendance_percentage = (present_days / total_attendance * 100) if total_attendance > 0 else 0
    average_grade = sum(result.score for result in exam_results) / len(exam_results) if exam_results else 0

    return {
        'user': {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'role': user.role,
            'school': student.school.name,
        },
        'student': {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'admission_number': student.admission_number,
            'classroom': student.classroom.name if student.classroom else None,
            'status': student.status,
            'gender': student.gender,
        },
        'summary': {
            'attendance_percentage': round(attendance_percentage, 1),
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'average_grade': round(average_grade, 1),
            'subjects_count': len(classroom_subjects),
            'unread_messages': unread_messages,
        },
        'subjects': classroom_subjects,
        'results': [
            {
                'id': result.id,
                'exam_name': result.exam.name,
                'subject_name': result.subject.name,
                'subject_code': result.subject.code,
                'score': result.score,
                'recorded_at': result.created_at,
            }
            for result in exam_results
        ],
        'attendance': [
            {
                'id': row.id,
                'date': row.date,
                'status': row.status,
            }
            for row in attendance_records[:20]
        ],
        'ai_insight': {
            'attendance_risk': getattr(insight, 'attendance_risk', 0),
            'performance_risk': getattr(insight, 'performance_risk', 0),
            'overall_risk': getattr(insight, 'overall_risk', 0),
            'risk_level': insight.get_risk_level() if insight else 'LOW',
            'flagged_subjects': getattr(insight, 'flagged_subjects', []),
            'recommendations': insight.get_recommendations() if insight else [],
        },
        'settings': {setting.key: setting.value for setting in settings},
    }
