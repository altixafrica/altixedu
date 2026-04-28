from apps.academics.models import Classroom, Subject
from apps.accounts.models import User
from apps.finance.models import StudentFee
from apps.notifications.models import RoleSetting, StudentAIInsights
from apps.students.models import Student


def build_school_admin_dashboard_payload(user):
    school = user.school
    students = Student.objects.filter(school=school).select_related('classroom')
    teachers = User.objects.filter(school=school, role='teacher')
    classrooms = Classroom.objects.filter(school=school)
    subjects = Subject.objects.filter(school=school)

    fees = StudentFee.objects.filter(student__in=students).select_related('fee')
    total_fees = sum(fee.fee.amount for fee in fees)
    total_paid = sum(fee.amount_paid for fee in fees)
    total_outstanding = total_fees - total_paid

    ai_insights = StudentAIInsights.objects.filter(student__in=students).select_related('student', 'student__classroom').order_by('-performance_risk')
    at_risk_students = [
        {
            'student_id': insight.student.id,
            'student_name': f'{insight.student.first_name} {insight.student.last_name}',
            'admission_number': insight.student.admission_number,
            'classroom': insight.student.classroom.name if insight.student.classroom else None,
            'attendance_risk': insight.attendance_risk,
            'performance_risk': insight.performance_risk,
            'low_attendance': insight.low_attendance,
            'low_performance': insight.low_performance,
            'flagged_subjects': insight.flagged_subjects,
        }
        for insight in ai_insights
        if insight.low_attendance or insight.low_performance
    ]

    settings = RoleSetting.objects.filter(role='admin', school=school)

    return {
        'user': {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'role': user.role,
            'school': school.name,
        },
        'statistics': {
            'total_students': students.count(),
            'total_teachers': teachers.count(),
            'total_classrooms': classrooms.count(),
            'total_subjects': subjects.count(),
            'at_risk_students': len(at_risk_students),
        },
        'finance': {
            'total_fees': total_fees,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding,
            'collection_percentage': (total_paid / total_fees * 100) if total_fees > 0 else 0,
        },
        'students': [
            {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'admission_number': student.admission_number,
                'classroom': student.classroom.name if student.classroom else None,
                'status': student.status,
                'gender': student.gender,
            }
            for student in students[:50]
        ],
        'teachers': [
            {
                'id': teacher.id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'email': teacher.email,
            }
            for teacher in teachers
        ],
        'classrooms': [
            {
                'id': classroom.id,
                'name': classroom.name,
                'grade_level': classroom.grade_level,
                'student_count': classroom.students.count(),
            }
            for classroom in classrooms
        ],
        'subjects': [
            {
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
            }
            for subject in subjects
        ],
        'at_risk_alerts': at_risk_students[:20],
        'settings': {setting.key: setting.value for setting in settings},
    }
