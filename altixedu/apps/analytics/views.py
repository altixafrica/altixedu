from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from apps.notifications.models import StudentAIInsights
from apps.students.models import Student
from apps.attendance.models import Attendance
from apps.academics.models import ExamResult
from apps.finance.models import StudentFee
from apps.schools.models import School
from apps.accounts.models import User
from .models import AnalyticsDashboard, SchoolPerformanceMetric


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def advanced_analytics_dashboard(request):
    """Advanced analytics dashboard for school admins and superadmins"""
    user = request.user
    
    if user.role not in ['admin', 'superadmin']:
        return Response(
            {'error': 'Only admins can access advanced analytics'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        if user.role == 'superadmin':
            # Superadmin sees platform-wide metrics
            data = _get_platform_analytics()
        else:
            # Admin sees school-specific metrics
            data = _get_school_analytics(user.school)
        return Response(data)
    except Exception as e:
        return Response(
            {'error': f'Error calculating analytics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _get_school_analytics(school):
    """Get comprehensive analytics for a school"""
    students = Student.objects.filter(school=school)
    teachers = User.objects.filter(school=school, role='teacher')
    
    # AI Risk Analysis
    ai_insights = StudentAIInsights.objects.filter(student__in=students)
    students_at_risk = ai_insights.filter(
        Q(low_attendance=True) | Q(low_performance=True)
    ).count()
    
    avg_attendance_risk = ai_insights.aggregate(Avg('attendance_risk')).get('attendance_risk__avg') or 0
    avg_performance_risk = ai_insights.aggregate(Avg('performance_risk')).get('performance_risk__avg') or 0
    
    # Attendance Analytics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_attendance = Attendance.objects.filter(
        student__school=school,
        date__gte=thirty_days_ago.date()
    )
    attendance_count = recent_attendance.filter(status='present').count()
    total_attendance = recent_attendance.count()
    attendance_rate = ((attendance_count / total_attendance * 100) if total_attendance > 0 else 0)
    
    # Performance Analytics  
    exam_results = ExamResult.objects.filter(student__school=school)
    avg_score = exam_results.aggregate(Avg('score')).get('score__avg') or 0
    
    # Finance Analytics
    fees = StudentFee.objects.filter(student__in=students)
    total_due = fees.aggregate(Sum('fee__amount')).get('fee__amount__sum') or 0
    total_paid = fees.aggregate(Sum('amount_paid')).get('amount_paid__sum') or 0
    collection_rate = ((total_paid / total_due * 100) if total_due > 0 else 0)
    
    return {
        'school': {
            'id': school.id,
            'name': school.name,
        },
        'students': {
            'total': students.count(),
            'at_risk': students_at_risk,
        },
        'attendance': {
            'average_rate': round(float(attendance_rate), 2),
            'present': attendance_count,
            'absent': total_attendance - attendance_count,
        },
        'performance': {
            'average_score': round(float(avg_score), 2),
            'total_exams': exam_results.count(),
        },
        'finance': {
            'total_due': float(total_due),
            'total_collected': float(total_paid),
            'collection_rate': round(float(collection_rate), 2),
        },
        'risk_analysis': {
            'avg_attendance_risk': round(float(avg_attendance_risk), 2),
            'avg_performance_risk': round(float(avg_performance_risk), 2),
        },
        'staff': {
            'total_teachers': teachers.count(),
        },
    }


def _get_platform_analytics():
    """Get platform-wide analytics for superadmins"""
    schools = School.objects.all()
    total_students = Student.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    
    # AI Risk (all schools)
    all_insights = StudentAIInsights.objects.all()
    all_at_risk = all_insights.filter(
        Q(low_attendance=True) | Q(low_performance=True)
    ).count()
    
    # Attendance (all schools)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    all_attendance = Attendance.objects.filter(date__gte=thirty_days_ago.date())
    present_count = all_attendance.filter(status='present').count()
    total_count = all_attendance.count()
    platform_attendance_rate = ((present_count / total_count * 100) if total_count > 0 else 0)
    
    # Finance (all schools)
    all_fees = StudentFee.objects.all()
    total_due = all_fees.aggregate(Sum('fee__amount')).get('fee__amount__sum') or 0
    total_paid = all_fees.aggregate(Sum('amount_paid')).get('amount_paid__sum') or 0
    collection_rate = ((total_paid / total_due * 100) if total_due > 0 else 0)
    
    return {
        'platform': {
            'total_schools': schools.count(),
            'total_students': total_students,
            'total_teachers': total_teachers,
        },
        'students': {
            'total': total_students,
            'at_risk': all_at_risk,
        },
        'attendance': {
            'platform_average_rate': round(float(platform_attendance_rate), 2),
        },
        'finance': {
            'total_due': float(total_due),
            'total_collected': float(total_paid),
            'collection_rate': round(float(collection_rate), 2),
        },
    }
