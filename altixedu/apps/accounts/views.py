from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Sum, Q, Count, F
from .models import User
from .serializers import UserSerializer, CreateUserSerializer, CreateMinistryAdminSerializer, PasswordResetSerializer, MinistryAdminLoginSerializer
from .permissions import IsParent, IsSchoolAdmin
from apps.students.models import Student
from apps.finance.models import StudentFee
from apps.notifications.models import StudentAIInsights, RoleSetting, Message
from apps.attendance.models import Attendance
from apps.schools.models import School


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
            try:
                user_obj = User.objects.get(email=email)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass
        
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
                'name': user.school.name
            } if user.school else None,
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
                'pay_fees': True,
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
                'name': user.school.name
            } if user.school else None,
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
        if user.role == 'superadmin':
            return User.objects.all()
        elif user.school and user.role in ['admin']:
            return User.objects.filter(school=user.school)
        return User.objects.none()
    
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
        
        # For bursar/admin: show their school's financial data
        school = user.school
        student_fees = StudentFee.objects.filter(school=school).select_related('student', 'fee')
        
        # Calculate metrics
        total_due = student_fees.aggregate(Sum('fee__amount'))['fee__amount__sum'] or 0
        total_paid = student_fees.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        total_balance = total_due - total_paid
        
        # Group by payment status
        fees_by_status = [
            {
                'status': 'paid',
                'count': student_fees.filter(amount_paid__gte=F('fee__amount')).count(),
                'total': student_fees.filter(amount_paid__gte=F('fee__amount')).aggregate(
                    total=Sum('amount_paid')
                )['total'] or 0
            },
            {
                'status': 'partial',
                'count': student_fees.filter(
                    amount_paid__gt=0,
                    amount_paid__lt=F('fee__amount')
                ).count(),
                'total': student_fees.filter(
                    amount_paid__gt=0,
                    amount_paid__lt=F('fee__amount')
                ).aggregate(total=Sum('amount_paid'))['total'] or 0
            },
            {
                'status': 'unpaid',
                'count': student_fees.filter(amount_paid=0).count(),
                'total': student_fees.filter(amount_paid=0).aggregate(
                    total=Sum('fee__amount')
                )['total'] or 0
            }
        ]
        
        return Response({
            'school': {
                'id': school.id,
                'name': school.name
            },
            'financial_summary': {
                'total_due': float(total_due),
                'total_paid': float(total_paid),
                'balance': float(total_balance),
                'collection_rate': (total_paid / total_due * 100) if total_due > 0 else 0
            },
            'fees_by_status': fees_by_status,
            'total_students': Student.objects.filter(school=school).count(),
        })


class ParentDashboardView(APIView):
    """
    Parent dashboard showing all linked children, fees, attendance, AI insights, and settings.
    """
    permission_classes = [permissions.IsAuthenticated, IsParent]

    def get(self, request):
        user = request.user
        
        # 1. Fetch all children linked to this parent
        students = Student.objects.filter(parents=user).select_related('classroom', 'school')
        
        # 2. Fetch fees per student with aggregations
        fees_data = []
        for student in students:
            student_fees = StudentFee.objects.filter(student=student)
            total_due = sum(fee.fee.amount for fee in student_fees)
            total_paid = sum(fee.amount_paid for fee in student_fees)
            balance = total_due - total_paid
            fees_data.append({
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}",
                'total_due': total_due,
                'amount_paid': total_paid,
                'balance': balance,
                'paid': balance <= 0
            })
        
        # 3. Fetch attendance for all children (recent 30 days)
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import F
        import models
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        attendance_data = []
        for student in students:
            attendance_records = Attendance.objects.filter(
                student=student,
                created_at__gte=thirty_days_ago
            ).order_by('-date')
            attendance_data.append({
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}",
                'total_days': attendance_records.count(),
                'present_days': attendance_records.filter(status='present').count(),
                'absent_days': attendance_records.filter(status='absent').count(),
                'late_days': attendance_records.filter(status='late').count(),
                'attendance_percentage': (
                    (attendance_records.filter(status='present').count() / 
                     attendance_records.count() * 100) if attendance_records.count() > 0 else 0
                )
            })
        
        # 4. Fetch AI insights per student
        ai_insights_data = []
        for student in students:
            ai_insight = StudentAIInsights.objects.filter(student=student).first()
            if ai_insight:
                ai_insights_data.append({
                    'student_id': student.id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'attendance_risk': ai_insight.attendance_risk,
                    'performance_risk': ai_insight.performance_risk,
                    'low_attendance': ai_insight.low_attendance,
                    'low_performance': ai_insight.low_performance,
                    'flagged_subjects': ai_insight.flagged_subjects
                })
        
        # 5. Fetch parent settings
        settings = RoleSetting.objects.filter(role='parent', school=user.school)
        settings_data = {s.key: s.value for s in settings}
        
        # 6. Fetch unread message count
        unread_messages = Message.objects.filter(
            receiver=user,
            read=False,
            school=user.school
        ).count()
        
        # 7. Build response
        response_data = {
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'school': user.school.name if user.school else None
            },
            'children': [
                {
                    'id': s.id,
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'admission_number': s.admission_number,
                    'classroom': s.classroom.name if s.classroom else None,
                    'status': s.status,
                    'gender': s.gender
                } for s in students
            ],
            'fees': fees_data,
            'attendance': attendance_data,
            'ai_insights': ai_insights_data,
            'messages': {
                'unread_count': unread_messages
            },
            'settings': settings_data
        }
        return Response(response_data, status=status.HTTP_200_OK)


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
            # Only superadmin can force password reset
            if request.user.role != 'superadmin':
                return Response(
                    {'error': 'Only superadmin can force password resets'},
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
        if user.role == 'superadmin':
            # Superadmin can create schools anywhere
            pass
        elif user.role == 'ministry_admin':
            # Ministry admin can create schools in their state only
            request_state = request.data.get('state')
            if request_state != user.ministry.state_or_province:
                return Response(
                    {'error': f'Ministry admin can only create schools in {user.ministry.state_or_province}'},
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
                {'error': 'Only superadmin, ministry admin, or school admin can create schools'},
                status=status.HTTP_403_FORBIDDEN
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
            )
            
            return Response(
                {
                    'id': school.id,
                    'name': school.name,
                    'subdomain': school.subdomain,
                    'email': school.email,
                    'phone': school.phone,
                    'address': school.address,
                    'city': school.city,
                    'state': school.state,
                    'country': school.country,
                    'website': school.website,
                    'timezone': school.timezone,
                    'language': school.language,
                    'message': f'School "{school.name}" created successfully with state "{school.state}"'
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Error creating school: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
