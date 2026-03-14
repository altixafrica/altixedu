from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count, Q
from apps.accounts.permissions import IsSchoolAdmin
from apps.accounts.models import User
from apps.students.models import Student
from apps.finance.models import StudentFee, Fee
from apps.notifications.models import StudentAIInsights, RoleSetting
from apps.academics.models import Classroom, Subject, TeacherSubject
from apps.notifications.serializers import (
    StudentAIInsightsSerializer,
    RoleSettingSerializer
)


class SchoolAdminDashboardView(APIView):
    """
    School Admin dashboard showing all school data, financial summary, alerts, and settings.
    """
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        user = request.user
        school = user.school
        
        if not school:
            return Response(
                {"detail": "School Admin must be linked to a school"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 1. Fetch students, teachers, classrooms, subjects
        students = Student.objects.filter(school=school)
        teachers = User.objects.filter(school=school, role='teacher')
        classrooms = Classroom.objects.filter(school=school)
        subjects = Subject.objects.filter(school=school)
        
        # 2. Financial summary
        fees = StudentFee.objects.filter(student__in=students)
        total_fees = sum(fee.fee.amount for fee in fees)
        total_paid = sum(fee.amount_paid for fee in fees)
        total_outstanding = total_fees - total_paid
        
        # 3. Fetch AI insights for at-risk students
        ai_insights = StudentAIInsights.objects.filter(
            student__in=students
        ).order_by('-performance_risk')
        
        at_risk_students = []
        for insight in ai_insights:
            if insight.low_attendance or insight.low_performance:
                at_risk_students.append({
                    'student_id': insight.student.id,
                    'student_name': f"{insight.student.first_name} {insight.student.last_name}",
                    'admission_number': insight.student.admission_number,
                    'classroom': insight.student.classroom.name if insight.student.classroom else None,
                    'attendance_risk': insight.attendance_risk,
                    'performance_risk': insight.performance_risk,
                    'low_attendance': insight.low_attendance,
                    'low_performance': insight.low_performance,
                    'flagged_subjects': insight.flagged_subjects
                })
        
        # 4. Fetch school admin settings
        settings = RoleSetting.objects.filter(role='admin', school=school)
        settings_data = {s.key: s.value for s in settings}
        
        # 5. Build response
        response_data = {
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'school': school.name
            },
            'statistics': {
                'total_students': students.count(),
                'total_teachers': teachers.count(),
                'total_classrooms': classrooms.count(),
                'total_subjects': subjects.count(),
                'at_risk_students': len(at_risk_students)
            },
            'finance': {
                'total_fees': total_fees,
                'total_paid': total_paid,
                'total_outstanding': total_outstanding,
                'collection_percentage': (
                    (total_paid / total_fees * 100) if total_fees > 0 else 0
                )
            },
            'students': [
                {
                    'id': s.id,
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'admission_number': s.admission_number,
                    'classroom': s.classroom.name if s.classroom else None,
                    'status': s.status,
                    'gender': s.gender
                } for s in students[:50]  # Limit to first 50 for performance
            ],
            'teachers': [
                {
                    'id': t.id,
                    'first_name': t.first_name,
                    'last_name': t.last_name,
                    'email': t.email
                } for t in teachers
            ],
            'classrooms': [
                {
                    'id': c.id,
                    'name': c.name,
                    'grade_level': c.grade_level,
                    'student_count': c.students.count()
                } for c in classrooms
            ],
            'subjects': [
                {
                    'id': s.id,
                    'name': s.name,
                    'code': s.code
                } for s in subjects
            ],
            'at_risk_alerts': at_risk_students[:20],  # Top 20 at-risk students
            'settings': settings_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
