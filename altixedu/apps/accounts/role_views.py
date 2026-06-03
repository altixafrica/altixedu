"""
Views for Custom Roles and Advanced Management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from apps.accounts.role_models import (
    CustomRole,
    RoleUserAssignment,
    StudentClassroomAssignment,
    ParentStudentLink
)
from apps.accounts.role_serializers import (
    CustomRoleSerializer,
    RoleUserAssignmentSerializer,
    StudentClassroomAssignmentSerializer,
    ParentStudentLinkSerializer
)
from apps.accounts.permissions import IsSchoolAdmin, IsSuperAdmin
from apps.students.models import Student
from audit import log_action
from bulk_import import BulkUserImporter
from report_generation import AttendanceReportGenerator


class CustomRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom roles.
    Admins can define custom roles for their school.
    """
    serializer_class = CustomRoleSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    
    def get_queryset(self):
        """Get roles for user's school"""
        user = self.request.user
        
        if user.role == 'superadmin':
            return CustomRole.objects.all()
        else:
            return CustomRole.objects.filter(school=user.school)
    
    def perform_create(self, serializer):
        """Create role and assign to school"""
        instance = serializer.save(
            school=self.request.user.school,
            created_by=self.request.user
        )
        
        log_action(
            user=self.request.user,
            action_type='custom_role_create',
            action_description=f'Custom role created: {instance.name}',
            content_type='CustomRole',
            object_id=instance.id,
            object_name=instance.name,
            request=self.request
        )
    
    def perform_destroy(self, instance):
        """Log role deletion"""
        log_action(
            user=self.request.user,
            action_type='custom_role_delete',
            action_description=f'Custom role deleted: {instance.name}',
            content_type='CustomRole',
            object_id=instance.id,
            object_name=instance.name,
            request=self.request
        )
        super().perform_destroy(instance)


class RoleUserAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for assigning custom roles to users.
    """
    serializer_class = RoleUserAssignmentSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    
    def get_queryset(self):
        """Get assignments for user's school"""
        user = self.request.user
        
        if user.role == 'superadmin':
            return RoleUserAssignment.objects.all()
        else:
            return RoleUserAssignment.objects.filter(
                role__school=user.school
            )
    
    def perform_create(self, serializer):
        """Create assignment and log it"""
        instance = serializer.save(assigned_by=self.request.user)
        
        log_action(
            user=self.request.user,
            action_type='role_assignment_create',
            action_description=f'Role {instance.role.name} assigned to {instance.user.get_full_name()}',
            content_type='RoleUserAssignment',
            object_id=instance.id,
            object_name=f'{instance.user.get_full_name()} - {instance.role.name}',
            request=self.request
        )


class StudentClassroomAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student-to-classroom assignments.
    Supports multiple classrooms and academic year scoping.
    """
    serializer_class = StudentClassroomAssignmentSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    
    def get_queryset(self):
        """Get assignments for user's school"""
        user = self.request.user
        
        if user.role == 'superadmin':
            queryset = StudentClassroomAssignment.objects.all()
        else:
            queryset = StudentClassroomAssignment.objects.filter(
                student__school=user.school
            )
        
        # Filter by classroom if provided
        classroom_id = self.request.query_params.get('classroom_id')
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)
        
        # Filter by academic year if provided
        academic_year = self.request.query_params.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        
        # Filter by active/inactive
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('classroom', 'roll_number')
    
    def perform_create(self, serializer):
        """Create assignment"""
        instance = serializer.save()
        
        log_action(
            user=self.request.user,
            action_type='student_classroom_assign',
            action_description=f'{instance.student} assigned to {instance.classroom}',
            content_type='StudentClassroomAssignment',
            object_id=instance.id,
            object_name=str(instance),
            request=self.request
        )
    
    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """
        Bulk assign students to classroom.
        
        Request format:
        {
            "classroom_id": 1,
            "academic_year": "2024-2025",
            "assignments": [
                {"student_id": 1, "roll_number": 1},
                {"student_id": 2, "roll_number": 2}
            ]
        }
        """
        classroom_id = request.data.get('classroom_id')
        academic_year = request.data.get('academic_year')
        assignments = request.data.get('assignments', [])
        
        if not classroom_id or not academic_year or not assignments:
            return Response(
                {'error': 'classroom_id, academic_year, and assignments are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = []
        errors = []
        
        for item in assignments:
            try:
                student_id = item.get('student_id')
                roll_number = item.get('roll_number')
                
                student = Student.objects.get(id=student_id, school=request.user.school)
                
                assignment, created_flag = StudentClassroomAssignment.objects.update_or_create(
                    student_id=student_id,
                    classroom_id=classroom_id,
                    academic_year=academic_year,
                    defaults={'roll_number': roll_number, 'is_active': True}
                )
                
                created.append({
                    'student_id': student_id,
                    'assignment_id': assignment.id,
                    'created': created_flag
                })
            
            except Student.DoesNotExist:
                errors.append(f'Student {item.get("student_id")} not found')
            except Exception as e:
                errors.append(f'Error processing student {item.get("student_id")}: {str(e)}')
        
        return Response({
            'created': created,
            'errors': errors,
            'total': len(created),
            'failed': len(errors)
        })
    
    @action(detail=False, methods=['get'])
    def by_classroom(self, request):
        """Get all students in a classroom for a specific academic year"""
        classroom_id = request.query_params.get('classroom_id')
        academic_year = request.query_params.get('academic_year')
        
        if not classroom_id:
            return Response(
                {'error': 'classroom_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            classroom_id=classroom_id,
            is_active=True
        )
        
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ParentStudentLinkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing parent-student relationships.
    Supports multiple parents per student and vice versa.
    """
    serializer_class = ParentStudentLinkSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    
    def get_queryset(self):
        """Get links for user's school"""
        user = self.request.user
        
        if user.role == 'superadmin':
            queryset = ParentStudentLink.objects.all()
        else:
            queryset = ParentStudentLink.objects.filter(
                student__school=user.school
            )
        
        # Filter by parent if provided
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        # Filter by student if provided
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset.order_by('student', '-is_primary')
    
    def perform_create(self, serializer):
        """Create link"""
        instance = serializer.save()
        
        log_action(
            user=self.request.user,
            action_type='parent_student_link',
            action_description=f'{instance.parent.get_full_name()} linked to {instance.student}',
            content_type='ParentStudentLink',
            object_id=instance.id,
            object_name=str(instance),
            request=self.request
        )
    
    @action(detail=False, methods=['post'])
    def bulk_link(self, request):
        """
        Bulk link multiple students to a parent.
        
        Request format:
        {
            "parent_id": 1,
            "student_ids": [1, 2, 3],
            "relationship": "mother"
        }
        """
        parent_id = request.data.get('parent_id')
        student_ids = request.data.get('student_ids', [])
        relationship = request.data.get('relationship', 'guardian')
        
        if not parent_id or not student_ids:
            return Response(
                {'error': 'parent_id and student_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = []
        errors = []
        
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id, school=request.user.school)
                
                link, created_flag = ParentStudentLink.objects.update_or_create(
                    parent_id=parent_id,
                    student_id=student_id,
                    defaults={'relationship': relationship, 'is_active': True}
                )
                
                created.append({
                    'student_id': student_id,
                    'link_id': link.id,
                    'created': created_flag
                })
            
            except Student.DoesNotExist:
                errors.append(f'Student {student_id} not found')
            except Exception as e:
                errors.append(f'Error linking student {student_id}: {str(e)}')
        
        return Response({
            'created': created,
            'errors': errors,
            'total': len(created),
            'failed': len(errors)
        })
    
    @action(detail=False, methods=['get'])
    def by_parent(self, request):
        """Get all students linked to a parent"""
        parent_id = request.query_params.get('parent_id')
        
        if not parent_id:
            return Response(
                {'error': 'parent_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            parent_id=parent_id,
            is_active=True
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get all parents linked to a student"""
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            student_id=student_id,
            is_active=True
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
