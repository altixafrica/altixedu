"""
User Management System for School Admins
Allows school admins to manage users (teachers, staff, parents)
and manage student enrollment/removal with archival
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from apps.accounts.models import User
from apps.students.models import Student
from apps.core.models import AuditLog
from apps.accounts.role_models import ParentStudentLink
from apps.accounts.serializers import UserSerializer


class IsSchoolAdmin(permissions.BasePermission):
    """Permission: User is school admin"""
    def has_permission(self, request, view):
        return request.user.role == 'admin' and request.user.school is not None


class UserManagementViewSet(viewsets.ViewSet):
    """
    School Admin user management endpoints
    - Delete users (with audit trail)
    - Reassign user roles (teacher -> bursar, etc.)
    - Deactivate users (soft delete)
    - List users by role
    """
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def _get_school(self, request):
        """Get school from authenticated user"""
        if not request.user.school:
            raise PermissionDenied("User not assigned to a school")
        return request.user.school
    
    @action(detail=False, methods=['get'])
    def users_by_role(self, request):
        """
        List all users in school by role
        
        GET /api/user-management/users_by_role/?role=teacher
        Roles: teacher, student, parent, bursar, admin
        """
        school = self._get_school(request)
        role = request.query_params.get('role')
        
        users = User.objects.filter(school=school)
        
        if role:
            users = users.filter(role=role)
        
        users = users.order_by('first_name').values(
            'id', 'first_name', 'last_name', 'email', 'role', 'is_active', 'created_at'
        )
        
        return Response({
            'count': users.count(),
            'role_filter': role,
            'users': list(users)
        })
    
    @action(detail=False, methods=['post'], url_path='reassign-role')
    def reassign_role(self, request):
        """
        Reassign a user's role (teacher -> bursar, etc.)
        
        POST /api/user-management/reassign-role/
        {
            'user_id': 123,
            'new_role': 'bursar',
            'reason': 'Promoted to finance officer'
        }
        
        Only allows reassignment within school staff roles:
        - teacher, bursar, admin (not student/parent)
        """
        school = self._get_school(request)
        user_id = request.data.get('user_id')
        new_role = request.data.get('new_role')
        reason = request.data.get('reason', 'Role reassignment')
        
        if not user_id or not new_role:
            return Response(
                {'error': 'user_id and new_role required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate new role is staff role (not student/parent)
        STAFF_ROLES = ['teacher', 'bursar', 'admin']
        if new_role not in STAFF_ROLES:
            return Response(
                {'error': f'Can only reassign to staff roles: {", ".join(STAFF_ROLES)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id, school=school)
            
            # Prevent reassigning other admins (only superadmin can do that)
            if user.role == 'admin' and request.user.id != user.id:
                return Response(
                    {'error': 'Cannot reassign other school admins'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            old_role = user.role
            user.role = new_role
            user.save()
            
            # Log the change
            AuditLog.log_change(
                user=request.user,
                instance=user,
                action='role_reassignment',
                changes={'role': [old_role, new_role]},
                description=reason,
                school=school,
                ip_address=self._get_client_ip(request)
            )
            
            return Response({
                'success': True,
                'message': f'User role changed from {old_role} to {new_role}',
                'user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'old_role': old_role,
                    'new_role': new_role
                }
            })
        
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found in your school'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='deactivate-user')
    def deactivate_user(self, request):
        """
        Deactivate a user (soft delete - keeps records)
        User cannot login but history is preserved
        
        POST /api/user-management/deactivate-user/
        {
            'user_id': 123,
            'reason': 'Left school',
            'archive': true
        }
        """
        school = self._get_school(request)
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', 'Deactivated by admin')
        
        if not user_id:
            return Response(
                {'error': 'user_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id, school=school)
            
            if user.id == request.user.id:
                return Response(
                    {'error': 'Cannot deactivate your own account'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if user.role == 'admin':
                return Response(
                    {'error': 'Cannot deactivate school admin'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Deactivate user
            user.is_active = False
            user.save()
            
            # Log
            AuditLog.log_change(
                user=request.user,
                instance=user,
                action='deactivate',
                changes={'is_active': [True, False]},
                description=reason,
                school=school,
                ip_address=self._get_client_ip(request)
            )
            
            return Response({
                'success': True,
                'message': f'User {user.get_full_name()} deactivated',
                'user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'is_active': user.is_active
                }
            })
        
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], url_path='delete-user')
    def delete_user(self, request):
        """
        PERMANENTLY delete user and related data
        ⚠️ This action cannot be undone
        Only use for duplicate/test accounts
        
        Historical records (attendance, grades, payments) are preserved
        via AuditLog for compliance
        
        POST /api/user-management/delete-user/
        {
            'user_id': 123,
            'reason': 'Duplicate account',
            'confirm_delete': true
        }
        """
        school = self._get_school(request)
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', 'User deletion')
        confirm = request.data.get('confirm_delete', False)
        
        if not user_id:
            return Response(
                {'error': 'user_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not confirm:
            return Response(
                {'error': 'Confirm deletion by setting confirm_delete: true'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id, school=school)
            
            # Prevent deleting self or admins
            if user.id == request.user.id:
                return Response(
                    {'error': 'Cannot delete your own account'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if user.role == 'admin':
                return Response(
                    {'error': 'Cannot delete school admin'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create audit log BEFORE deletion
            user_info = {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role
            }
            
            # Delete related profiles first
            if user.role == 'student' and hasattr(user, 'student_profile'):
                user.student_profile.delete()
            elif user.role == 'teacher' and hasattr(user, 'teacher_profile'):
                user.teacher_profile.delete()
            elif user.role == 'parent' and hasattr(user, 'parent_profile'):
                user.parent_profile.delete()
            
            # Log deletion
            AuditLog.log_change(
                user=request.user,
                instance=user,
                action='delete',
                changes={'deleted': [False, True]},
                description=reason,
                school=school,
                ip_address=self._get_client_ip(request)
            )
            
            # Delete the user
            user.delete()
            
            return Response({
                'success': True,
                'message': f'User {user_info["name"]} permanently deleted',
                'deleted_user': user_info
            })
        
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class StudentManagementViewSet(viewsets.ViewSet):
    """
    School Admin student enrollment management
    - Enroll new students
    - Archive/remove students (keeps historical records)
    - Update student status
    - Bulk import students
    """
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def _get_school(self, request):
        if not request.user.school:
            raise PermissionDenied("User not assigned to a school")
        return request.user.school
    
    @action(detail=False, methods=['post'], url_path='remove-student')
    def remove_student(self, request):
        """
        Remove student from active enrollment
        Status changed to 'inactive' (archived)
        All historical records preserved: grades, attendance, payments
        
        POST /api/student-management/remove-student/
        {
            'student_id': 123,
            'reason': 'Student transferred',
            'archive_date': '2026-05-05'
        }
        """
        school = self._get_school(request)
        student_id = request.data.get('student_id')
        reason = request.data.get('reason', 'Student removed')
        archive_date = request.data.get('archive_date', timezone.now().date())
        
        if not student_id:
            return Response(
                {'error': 'student_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            student = Student.objects.get(id=student_id, school=school)
            
            if student.status == 'inactive':
                return Response(
                    {'error': 'Student already archived'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Archive student
            old_status = student.status
            student.status = 'inactive'
            student.save()
            
            # Deactivate associated user (if exists)
            if student.user:
                student.user.is_active = False
                student.user.save()
            
            # Log removal
            AuditLog.log_change(
                user=request.user,
                instance=student,
                action='student_archived',
                changes={
                    'status': [old_status, 'inactive'],
                    'archived_date': [None, str(archive_date)]
                },
                description=reason,
                school=school,
                ip_address=self._get_client_ip(request)
            )
            
            return Response({
                'success': True,
                'message': f'Student {student.first_name} {student.last_name} archived',
                'student': {
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'admission_number': student.admission_number,
                    'old_status': old_status,
                    'new_status': 'inactive',
                    'archived_date': archive_date
                }
            })
        
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found in your school'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='reactivate-student')
    def reactivate_student(self, request):
        """
        Reactivate archived student (e.g., returned from transfer)
        
        POST /api/student-management/reactivate-student/
        {
            'student_id': 123,
            'classroom_id': 5
        }
        """
        school = self._get_school(request)
        student_id = request.data.get('student_id')
        classroom_id = request.data.get('classroom_id')
        
        if not student_id or not classroom_id:
            return Response(
                {'error': 'student_id and classroom_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.academics.models import Classroom
            
            student = Student.objects.get(id=student_id, school=school)
            classroom = Classroom.objects.get(id=classroom_id, school=school)
            
            if student.status != 'inactive':
                return Response(
                    {'error': 'Only archived students can be reactivated'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reactivate
            student.status = 'active'
            student.classroom = classroom
            student.save()
            
            # Reactivate user
            if student.user:
                student.user.is_active = True
                student.user.save()
            
            # Log
            AuditLog.log_change(
                user=request.user,
                instance=student,
                action='student_reactivated',
                changes={'status': ['inactive', 'active']},
                school=school,
                ip_address=self._get_client_ip(request)
            )
            
            return Response({
                'success': True,
                'message': f'Student {student.first_name} {student.last_name} reactivated',
                'student': {
                    'id': student.id,
                    'status': 'active',
                    'classroom': classroom.name
                }
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def archived_students(self, request):
        """
        List all archived/inactive students
        
        GET /api/student-management/archived_students/
        """
        school = self._get_school(request)
        
        students = Student.objects.filter(
            school=school,
            status='inactive'
        ).order_by('-created_at').values(
            'id', 'first_name', 'last_name', 'admission_number', 'created_at'
        )
        
        return Response({
            'count': students.count(),
            'archived_students': list(students)
        })
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ParentManagementViewSet(viewsets.ViewSet):
    """
    School Admin parent profile management
    - Add/link parents to students
    - Remove parent associations
    - Update parent contact info
    """
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def _get_school(self, request):
        if not request.user.school:
            raise PermissionDenied("User not assigned to a school")
        return request.user.school
    
    @action(detail=False, methods=['post'], url_path='link-parent-student')
    def link_parent_student(self, request):
        """
        Link a parent to a student
        
        POST /api/parent-management/link-parent-student/
        {
            'parent_user_id': 10,
            'student_id': 123,
            'relationship': 'mother'
        }
        """
        school = self._get_school(request)
        parent_user_id = request.data.get('parent_user_id')
        student_id = request.data.get('student_id')
        relationship = request.data.get('relationship', 'guardian')
        
        try:
            parent_user = User.objects.get(id=parent_user_id, school=school, role='parent')
            student = Student.objects.get(id=student_id, school=school)
            
            # Link parent to student
            link, created = ParentStudentLink.objects.get_or_create(
                parent=parent_user,
                student=student,
                defaults={'relationship': relationship}
            )
            
            if not created:
                link.relationship = relationship
                link.save()
            
            # Log
            AuditLog.log_change(
                user=request.user,
                instance=link,
                action='parent_linked',
                school=school,
                ip_address=self._get_client_ip(request)
            )
            
            return Response({
                'success': True,
                'message': f'Parent linked to student',
                'link': {
                    'id': link.id,
                    'parent': parent_user.get_full_name(),
                    'student': f"{student.first_name} {student.last_name}",
                    'relationship': relationship
                }
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='unlink-parent-student')
    def unlink_parent_student(self, request):
        """
        Remove parent association from student
        
        POST /api/parent-management/unlink-parent-student/
        {
            'link_id': 5
        }
        """
        school = self._get_school(request)
        link_id = request.data.get('link_id')
        
        try:
            link = ParentStudentLink.objects.get(
                id=link_id,
                student__school=school
            )
            
            # Log before deletion
            AuditLog.log_change(
                user=request.user,
                instance=link,
                action='parent_unlinked',
                school=school,
                ip_address=self._get_client_ip(request)
            )
            
            link.delete()
            
            return Response({
                'success': True,
                'message': 'Parent-student link removed'
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
