from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Sum, Q, Count, F, Prefetch
from .models import User
from .serializers import UserSerializer, CreateUserSerializer, CreateMinistryAdminSerializer, PasswordResetSerializer, MinistryAdminLoginSerializer
from .permissions import IsParent, IsSchoolAdmin
from apps.students.models import Student
from apps.finance.models import StudentFee
from apps.notifications.models import StudentAIInsights, RoleSetting, Message
from apps.attendance.models import Attendance
from apps.schools.models import School, Ministry
from apps.billing.provisioning import seed_school_subscription
from .dashboard_payloads import build_bursar_dashboard_payload, build_parent_dashboard_payload, build_student_dashboard_payload


class LoginView(APIView):
    """
    Role-based login endpoint for all user types.
    Returns token + user info + role-based permissions + school data.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Login with username/email and password.
        Returns: token, user_id, role, school, permissions
        """
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to authenticate by username or email
        user = None
        if username:
            user = authenticate(username=username, password=password)
        elif email:
            user_obj = User.objects.filter(email=email).select_related('school', 'ministry').first()
            if user_obj and user_obj.check_password(password):
                user = user_obj
        
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Build role-based response
        response_data = {
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
            },
            'role': user.role,
            'school': {
                'id': user.school.id,
                'name': user.school.name,
                'subdomain': user.school.subdomain,
                'full_domain': user.school.full_domain,
                'country': user.school.country,
                'school_type': user.school.school_type,
            } if user.school else None,
            'ministry': {
                'id': user.ministry.id,
                'name': user.ministry.name,
                'country': user.ministry.country,
                'state_or_province': user.ministry.state_or_province,
                'currency_code': user.ministry.currency_code,
            } if user.ministry else None,
            'permissions': self._get_role_permissions(user)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @staticmethod
    def _get_role_permissions(user):
        """
        Get role-based permissions and access levels.
        """
        permissions_map = {
            'superadmin': {
                'view_school_stats': True,
                'view_all_schools': True,
                'view_aggregate_data': True,  # Only counts, not details
                'manage_all_users': True,
                'access_government_features': True,
                'manage_billing': True,
                'view_all_reports': True,
                'system_administration': True,
                'create_ministry_admins': True,
            },
            'ministry_admin': {
                'view_state_dashboard': True,
                'view_all_schools_in_state': True,
                'view_state_statistics': True,
                'access_government_features': True,
                'view_state_reports': True,
                'view_state_finances': True,
                'manage_state_approvals': True,
                'view_audit_logs': True,
            },
            'admin': {
                'view_own_school': True,
                'manage_school_staff': True,
                'manage_students': True,
                'view_student_details': True,
                'access_government_features': True,
                'manage_billing': True,
                'view_school_reports': True,
                'manage_school_settings': True,
                'export_data': True,
            },
            'teacher': {
                'view_own_classroom': True,
                'view_classroom_students': True,
                'mark_attendance': True,
                'enter_grades': True,
                'view_student_performance': True,
                'send_messages': True,
                'access_ai_insights': True,
                'view_assignments': True,
            },
            'student': {
                'view_own_data': True,
                'view_own_grades': True,
                'view_own_attendance': True,
                'view_messages': True,
                'view_own_ai_insights': True,
                'view_assignments': True,
                'submit_assignments': True,
            },
            'parent': {
                'view_children': True,
                'view_children_grades': True,
                'view_children_attendance': True,
                'view_children_fees': True,
                'view_children_ai_insights': True,
                'send_messages': True,
                'view_fee_status': True,
            },
            'bursar': {
                'view_all_students': True,
                'manage_payments': True,
                'view_billing': True,
                'generate_invoices': True,
                'manage_fees': True,
                'access_finance_reports': True,
                'view_fee_status': True,
                'track_payments': True,
                'generate_receipts': True,
            }
        }
        return permissions_map.get(user.role, {})


class LogoutView(APIView):
    """
    Logout endpoint - invalidates token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Logout by deleting user token."""
        try:
            request.user.auth_token.delete()
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(APIView):
    """
    Get current authenticated user info.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user details with permissions."""
        user = request.user
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
            },
            'role': user.role,
            'school': {
                'id': user.school.id,
                'name': user.school.name,
                'subdomain': user.school.subdomain,
                'full_domain': user.school.full_domain,
                'country': user.school.country,
                'school_type': user.school.school_type,
            } if user.school else None,
            'ministry': {
                'id': user.ministry.id,
                'name': user.ministry.name,
                'country': user.ministry.country,
                'state_or_province': user.ministry.state_or_province,
                'currency_code': user.ministry.currency_code,
            } if user.ministry else None,
            'permissions': LoginView._get_role_permissions(user)
        })


class UserViewSet(viewsets.ModelViewSet):
    """User CRUD endpoint for admin user management."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use CreateUserSerializer for create/update, UserSerializer for list/retrieve."""
        if self.action in ['create', 'update', 'partial_update']:
            return CreateUserSerializer
        return UserSerializer

    def get_queryset(self):
        """Filter users by school for non-superadmins."""
        user = self.request.user
        role_filter = self.request.query_params.get('role')

        if user.role == 'superadmin':
            queryset = User.objects.select_related('school', 'ministry').all()
        elif user.school and user.role in ['admin']:
            queryset = User.objects.select_related('school', 'ministry').filter(school=user.school)
        else:
            return User.objects.none()

        if role_filter:
            queryset = queryset.filter(role=role_filter)

        return queryset.order_by('last_name', 'first_name', 'username')
    
    def create(self, request, *args, **kwargs):
        """
        Create new user with role assignment.
        Only admin/superadmin can create users.
        School auto-assigned to current user's school (unless superadmin).
        """
        # Check permissions
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can create users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Auto-assign school if not superadmin
        data = request.data.copy()
        if request.user.role != 'superadmin':
            data['school'] = request.user.school.id
            data.pop('ministry', None)
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update user details - only admin can update users in their school."""
        user_to_update = self.get_object()
        
        # Check permissions
        if request.user.role == 'admin' and user_to_update.school != request.user.school:
            return Response(
                {'error': 'You can only update users in your school'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent role/school changes via direct API (security)
        data = request.data.copy()
        if 'role' in data:
            return Response(
                {'error': 'Cannot change user role. Please contact superadmin.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'school' in data and request.user.role != 'superadmin':
            return Response(
                {'error': 'Only superadmin can change user school'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(user_to_update, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete user - only superadmin can delete users."""
        if request.user.role != 'superadmin':
            return Response(
                {'error': 'Only superadmin can delete users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)


class BursarDashboardView(APIView):
    """
    Bursar dashboard showing all school fees, payments, and financial overview.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role not in ['bursar', 'admin', 'superadmin']:
            return Response(
                {'error': 'Bursar access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # For superadmin: only show aggregate stats
        if user.role == 'superadmin':
            from apps.schools.models import School
            schools_data = []
            for school in School.objects.all():
                total_students = Student.objects.filter(school=school).count()
                total_fees = StudentFee.objects.filter(school=school).aggregate(
                    total=Sum('fee__amount')
                )['total'] or 0
                fees_collected = StudentFee.objects.filter(school=school).aggregate(
                    total=Sum('amount_paid')
                )['total'] or 0
                
                schools_data.append({
                    'school_id': school.id,
                    'school_name': school.name,
                    'students_enrolled': total_students,
                    'total_fees_due': float(total_fees),
                    'fees_collected': float(fees_collected),
                    'collection_rate': (fees_collected / total_fees * 100) if total_fees > 0 else 0
                })
            
            return Response({
                'role': 'superadmin',
                'access_level': 'aggregate_only',
                'schools_summary': schools_data
            })
        
        return Response(build_bursar_dashboard_payload(user))


class TeacherDashboardView(APIView):
    """
    Teacher dashboard showing classroom assignments, watchlist students, and work queue.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'teacher':
            return Response(
                {'error': 'Teacher access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.school:
            return Response(
                {'error': 'Teacher must be linked to a school'},
                status=status.HTTP_403_FORBIDDEN
            )

        teacher_profile = getattr(user, 'teacher_profile', None)
        if not teacher_profile:
            return Response(
                {'error': 'Teacher profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        from datetime import timedelta
        from django.utils import timezone
        from apps.academics.models import TeacherSubject, Classroom
        from apps.attendance.models import Attendance
        from apps.academics.models import ExamResult

        assignments = TeacherSubject.objects.filter(
            teacher=teacher_profile,
            classroom__school=user.school
        ).select_related('subject', 'classroom').order_by('classroom__name', 'subject__name')

        classroom_ids = list(assignments.values_list('classroom_id', flat=True).distinct())
        subject_ids = list(assignments.values_list('subject_id', flat=True).distinct())

        classrooms = (
            Classroom.objects.filter(id__in=classroom_ids)
            .select_related('class_teacher', 'academic_year')
            .order_by('name')
        )
        students = Student.objects.filter(
            school=user.school,
            classroom_id__in=classroom_ids
        ).select_related('classroom').order_by('classroom__name', 'last_name', 'first_name')

        ai_insights = StudentAIInsights.objects.filter(student__in=students)
        ai_map = {insight.student_id: insight for insight in ai_insights}

        attendance_window = timezone.now().date() - timedelta(days=30)
        attendance_rows = Attendance.objects.filter(
            student__in=students,
            date__gte=attendance_window
        ).values('student_id').annotate(
            total_days=Count('id'),
            present_days=Count('id', filter=Q(status='present')),
            absent_days=Count('id', filter=Q(status='absent')),
            late_days=Count('id', filter=Q(status='late')),
        )
        attendance_map = {row['student_id']: row for row in attendance_rows}

        classroom_subjects = {}
        for assignment in assignments:
            classroom_subjects.setdefault(assignment.classroom_id, []).append({
                'id': assignment.subject.id,
                'name': assignment.subject.name,
                'code': assignment.subject.code,
            })

        recent_messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            school=user.school
        ).select_related('sender', 'receiver', 'student').order_by('-sent_at')[:8]

        settings = RoleSetting.objects.filter(role='teacher', school=user.school)

        student_rows = []
        for student in students[:40]:
            insight = ai_map.get(student.id)
            attendance = attendance_map.get(student.id, {})
            total_days = attendance.get('total_days', 0) or 0
            present_days = attendance.get('present_days', 0) or 0
            attendance_percentage = (
                round((present_days / total_days) * 100, 1)
                if total_days > 0 else round(float(getattr(insight, 'attendance_percentage', 0) or 0), 1)
            )

            student_rows.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'admission_number': student.admission_number,
                'classroom': student.classroom.name if student.classroom else None,
                'attendance_percentage': attendance_percentage,
                'average_grade': round(float(getattr(insight, 'average_grade', 0) or 0), 1),
                'overall_risk': round(float(getattr(insight, 'overall_risk', 0) or 0), 2),
                'risk_level': insight.get_risk_level() if insight else 'UNKNOWN',
                'flagged_subjects': getattr(insight, 'flagged_subjects', []),
            })

        response_data = {
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'school': user.school.name,
            },
            'summary': {
                'classrooms_count': len(classroom_ids),
                'subjects_count': len(subject_ids),
                'students_count': students.count(),
                'unread_messages': Message.objects.filter(
                    receiver=user,
                    read=False,
                    school=user.school
                ).count(),
                'at_risk_students': ai_insights.filter(overall_risk__gte=0.5).count(),
                'attendance_entries_last_30_days': Attendance.objects.filter(
                    recorded_by=user,
                    date__gte=attendance_window
                ).count(),
                'results_entered': ExamResult.objects.filter(created_by=user).count(),
            },
            'classrooms': [
                {
                    'id': classroom.id,
                    'name': classroom.name,
                    'grade_level': classroom.grade_level,
                    'academic_year': classroom.academic_year.year if classroom.academic_year else None,
                    'student_count': classroom.students.count(),
                    'is_class_teacher': classroom.class_teacher_id == teacher_profile.id,
                    'subjects': classroom_subjects.get(classroom.id, []),
                }
                for classroom in classrooms
            ],
            'subject_assignments': [
                {
                    'subject_id': assignment.subject.id,
                    'subject_name': assignment.subject.name,
                    'subject_code': assignment.subject.code,
                    'classroom_id': assignment.classroom.id,
                    'classroom_name': assignment.classroom.name,
                    'grade_level': assignment.classroom.grade_level,
                }
                for assignment in assignments
            ],
            'students': student_rows,
            'ai_watchlist': [
                {
                    'student_id': insight.student.id,
                    'student_name': f"{insight.student.first_name} {insight.student.last_name}",
                    'classroom': insight.student.classroom.name if insight.student.classroom else None,
                    'attendance_risk': insight.attendance_risk,
                    'performance_risk': insight.performance_risk,
                    'overall_risk': insight.overall_risk,
                    'risk_level': insight.get_risk_level(),
                    'flagged_subjects': insight.flagged_subjects,
                }
                for insight in ai_insights.filter(overall_risk__gte=0.5).select_related('student')[:12]
            ],
            'recent_messages': [
                {
                    'id': message.id,
                    'direction': 'inbound' if message.receiver_id == user.id else 'outbound',
                    'counterpart_name': (
                        message.sender.get_full_name()
                        if message.receiver_id == user.id else message.receiver.get_full_name()
                    ),
                    'content': message.content,
                    'student_name': (
                        f"{message.student.first_name} {message.student.last_name}"
                        if message.student else None
                    ),
                    'read': message.read,
                    'sent_at': message.sent_at,
                }
                for message in recent_messages
            ],
            'settings': {setting.key: setting.value for setting in settings},
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ParentDashboardView(APIView):
    """
    Parent dashboard showing all linked children, fees, attendance, AI insights, and settings.
    """
    permission_classes = [permissions.IsAuthenticated, IsParent]

    def get(self, request):
        user = request.user

        return Response(build_parent_dashboard_payload(user), status=status.HTTP_200_OK)


class StudentDashboardView(APIView):
    """
    Student dashboard showing the student's own academics, attendance, alerts, and settings.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            return Response(
                {'error': 'Student access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        payload = build_student_dashboard_payload(user)
        if not payload:
            return Response(
                {'error': 'Student profile not found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(payload, status=status.HTTP_200_OK)


class CreateMinistryAdminView(APIView):
    """
    Super Admin creates Ministry Admin users.
    Endpoint: POST /api/auth/create-ministry-admin/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create new ministry admin user."""
        # Check if user is superadmin
        if request.user.role != 'superadmin':
            return Response(
                {'error': 'Only superadmin can create ministry admins'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CreateMinistryAdminSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    Password reset endpoint for users.
    - Users can reset their own password with old password
    - Super admin can force password reset without verification
    
    Endpoint: POST /api/auth/reset-password/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Reset user password."""
        serializer = PasswordResetSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']
        is_admin_reset = serializer.validated_data.get('is_admin_reset', False)
        
        # Validate permissions
        if is_admin_reset:
            # Superadmin can force reset globally; school admins can reset users in their school.
            if request.user.role not in ['superadmin', 'admin']:
                return Response(
                    {'error': 'Only admins can force password resets'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if request.user.role == 'admin' and user.school_id != request.user.school_id:
                return Response(
                    {'error': 'School admins can only reset passwords for users in their school'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            # User can only reset their own password
            if request.user.id != user.id:
                return Response(
                    {'error': 'You can only reset your own password'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Reset password
        user.set_password(new_password)
        user.save()
        
        # Invalidate existing tokens (force re-login)
        Token.objects.filter(user=user).delete()
        
        return Response({
            'message': 'Password reset successfully',
            'note': 'User must login again with new password',
            'user_email': user.email
        }, status=status.HTTP_200_OK)


class MinistryAdminLoginView(APIView):
    """Ministry admin login endpoint - returns ministry context."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle ministry admin login."""
        serializer = MinistryAdminLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class SchoolSetupView(APIView):
    """School setup endpoint - creates schools with mandatory state collection."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a new school with state collection."""
        # Check role-based permissions
        user = request.user
        allowed_school_types = [choice[0] for choice in School.SCHOOL_TYPE_CHOICES]
        requested_school_type = request.data.get('school_type', 'private')
        selected_ministry = None

        if user.role == 'superadmin':
            # Superadmin can create schools anywhere
            ministry_id = request.data.get('ministry_id')
            if ministry_id:
                try:
                    selected_ministry = Ministry.objects.get(id=ministry_id)
                except Ministry.DoesNotExist:
                    return Response(
                        {'error': 'Selected ministry does not exist'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        elif user.role == 'ministry_admin':
            # Ministry admin can create schools in their state only
            selected_ministry = user.ministry
            if not selected_ministry:
                return Response(
                    {'error': 'Ministry admin must be linked to a ministry'},
                    status=status.HTTP_403_FORBIDDEN
                )
            request_state = request.data.get('state')
            if request_state != selected_ministry.state_or_province:
                return Response(
                    {'error': f'Ministry admin can only create schools in {selected_ministry.state_or_province}'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif user.role == 'admin':
            # School admin can only create/manage their own school
            return Response(
                {'error': 'School admins cannot create schools via this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            return Response(
                {'error': 'Only superadmin or ministry admin can create schools'},
                status=status.HTTP_403_FORBIDDEN
            )

        if requested_school_type not in allowed_school_types:
            return Response(
                {
                    'error': (
                        f'Invalid school_type "{requested_school_type}". '
                        f'Allowed values: {allowed_school_types}'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if selected_ministry:
            request_state = request.data.get('state')
            request_country = request.data.get('country')

            if request_state and request_state != selected_ministry.state_or_province:
                return Response(
                    {
                        'error': (
                            f'School state must match the ministry state '
                            f'({selected_ministry.state_or_province})'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if request_country and request_country != selected_ministry.country:
                return Response(
                    {
                        'error': (
                            f'School country must match the ministry country '
                            f'({selected_ministry.country})'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate required fields
        required_fields = ['name', 'subdomain', 'email', 'phone', 'address', 'city', 'state', 'country']
        missing_fields = [f for f in required_fields if f not in request.data or not request.data[f]]
        
        if missing_fields:
            return Response(
                {'error': f'Missing required fields: {missing_fields}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate uniqueness
        if School.objects.filter(subdomain=request.data['subdomain']).exists():
            return Response(
                {'error': 'School with this subdomain already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if School.objects.filter(email=request.data['email']).exists():
            return Response(
                {'error': 'School with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create school
        try:
            school = School.objects.create(
                name=request.data['name'],
                subdomain=request.data['subdomain'],
                email=request.data['email'],
                phone=request.data['phone'],
                address=request.data['address'],
                city=request.data['city'],
                state=request.data['state'],  # ENFORCED STATE COLLECTION
                country=request.data['country'],
                postal_code=request.data.get('postal_code', ''),
                website=request.data.get('website', ''),
                timezone=request.data.get('timezone', 'UTC'),
                language=request.data.get('language', 'en'),
                region=request.data.get('region', ''),
                school_type=requested_school_type,
                ministry=selected_ministry,
            )

            subscription = seed_school_subscription(school)
            
            return Response(
                {
                    'id': school.id,
                    'name': school.name,
                    'subdomain': school.subdomain,
                    'full_domain': school.full_domain,
                    'email': school.email,
                    'phone': school.phone,
                    'address': school.address,
                    'city': school.city,
                    'state': school.state,
                    'country': school.country,
                    'website': school.website,
                    'timezone': school.timezone,
                    'language': school.language,
                    'region': school.region,
                    'school_type': school.school_type,
                    'ministry': {
                        'id': selected_ministry.id,
                        'name': selected_ministry.name,
                        'country': selected_ministry.country,
                        'state_or_province': selected_ministry.state_or_province,
                    } if selected_ministry else None,
                    'subscription': {
                        'id': subscription.id,
                        'tier': subscription.tier.display_name if subscription and subscription.tier else None,
                        'status': subscription.status if subscription else None,
                        'payment_frequency': subscription.payment_frequency if subscription else None,
                    } if subscription else None,
                    'created_by_role': user.role,
                    'allowed_school_types': allowed_school_types,
                    'message': f'School "{school.name}" created successfully with state "{school.state}"'
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Error creating school: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
