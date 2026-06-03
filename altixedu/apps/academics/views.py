from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import (
    Classroom,
    Subject,
    TeacherSubject,
    Exam,
    ExamResult,
    AcademicYear,
    Term
)
from apps.students.models import Student
from .serializers import (
    ClassroomSerializer,
    SubjectSerializer,
    TeacherSubjectSerializer,
    ExamSerializer,
    ExamResultSerializer,
    AcademicYearSerializer,
    TermSerializer
)


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Classroom.objects.select_related('school').order_by('school__name', 'name')
        elif user.school:
            return Classroom.objects.filter(school=user.school).select_related('school').order_by('name')
        return Classroom.objects.none()

    def perform_create(self, serializer):
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Subject.objects.select_related('school').order_by('school__name', 'name')
        elif user.school:
            return Subject.objects.filter(school=user.school).select_related('school').order_by('name')
        return Subject.objects.none()

    def perform_create(self, serializer):
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()


class TeacherSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return TeacherSubject.objects.select_related('teacher', 'subject', 'classroom', 'school')
        elif user.school:
            return TeacherSubject.objects.filter(classroom__school=user.school).select_related(
                'teacher', 'subject', 'classroom', 'school'
            )
        return TeacherSubject.objects.none()

    def perform_create(self, serializer):
        school = self.request.user.school
        if school:
            serializer.save(school=school)
        else:
            serializer.save()


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Exam.objects.all()
        elif user.school:
            return Exam.objects.filter(school=user.school)
        return Exam.objects.none()

    def perform_create(self, serializer):
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()


class ExamResultViewSet(viewsets.ModelViewSet):
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return ExamResult.objects.select_related('exam', 'student', 'subject', 'created_by')
        elif user.school:
            return ExamResult.objects.filter(exam__school=user.school).select_related(
                'exam', 'student', 'subject', 'created_by'
            )
        return ExamResult.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='bulk-enter-scores')
    def bulk_enter_scores(self, request):
        """
        Bulk enter exam scores for a classroom/subject/exam
        
        POST /api/exam-results/bulk-enter-scores/
        {
            'exam_id': 1,
            'classroom_id': 1,
            'subject_id': 1,
            'scores': [
                {'student_id': 1, 'score': 85},
                {'student_id': 2, 'score': 92},
                {'student_id': 3, 'score': 78}
            ]
        }
        """
        exam_id = request.data.get('exam_id')
        classroom_id = request.data.get('classroom_id')
        subject_id = request.data.get('subject_id')
        scores = request.data.get('scores', [])
        
        # Validate inputs
        if not all([exam_id, classroom_id, subject_id, scores]):
            return Response(
                {'error': 'exam_id, classroom_id, subject_id, and scores are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get exam
            if request.user.role != 'teacher':
                return Response(
                    {'error': 'Only teachers can bulk enter scores'},
                    status=status.HTTP_403_FORBIDDEN
                )

            teacher = getattr(request.user, 'teacher_profile', None)
            if not teacher:
                return Response(
                    {'error': 'Teacher profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            exam = Exam.objects.get(id=exam_id, school=request.user.school)
            classroom = Classroom.objects.get(id=classroom_id, school=request.user.school)
            subject = Subject.objects.get(id=subject_id, school=request.user.school)
            
            # Verify teacher teaches this subject in this classroom
            has_permission = TeacherSubject.objects.filter(
                teacher=teacher,
                subject=subject,
                classroom=classroom
            ).exists()
            
            if not has_permission:
                return Response(
                    {'error': 'You do not teach this subject in this classroom'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Bulk create/update exam results
            created_count = 0
            updated_count = 0
            errors = []
            
            with transaction.atomic():
                for score_entry in scores:
                    try:
                        student_id = score_entry.get('student_id')
                        score_value = score_entry.get('score')
                        
                        if not student_id or score_value is None:
                            errors.append({
                                'student_id': student_id,
                                'error': 'student_id and score required'
                            })
                            continue
                        
                        try:
                            score_value = float(score_value)
                        except (TypeError, ValueError):
                            errors.append({
                                'student_id': student_id,
                                'error': 'Score must be a number'
                            })
                            continue

                        # Validate score range
                        if not (0 <= score_value <= 100):
                            errors.append({
                                'student_id': student_id,
                                'error': 'Score must be between 0 and 100'
                            })
                            continue
                        
                        try:
                            student = Student.objects.get(
                                id=student_id,
                                school=request.user.school,
                                classroom=classroom,
                            )
                        except Student.DoesNotExist:
                            errors.append({
                                'student_id': student_id,
                                'error': 'Student does not belong to this classroom'
                            })
                            continue

                        # Create or update exam result
                        exam_result, created = ExamResult.objects.update_or_create(
                            exam=exam,
                            student=student,
                            subject=subject,
                            defaults={
                                'score': score_value,
                                'created_by': request.user,
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    
                    except Exception as e:
                        errors.append({
                            'student_id': score_entry.get('student_id'),
                            'error': str(e)
                        })
            
            return Response({
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'errors': errors,
                'message': f'{created_count} scores created, {updated_count} updated'
            })
        
        except Exam.DoesNotExist:
            return Response(
                {'error': 'Exam not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Classroom.DoesNotExist:
            return Response(
                {'error': 'Classroom not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Subject.DoesNotExist:
            return Response(
                {'error': 'Subject not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Unable to enter scores right now.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='classroom-scores')
    def classroom_scores(self, request):
        """
        Get all exam scores for a classroom/exam/subject
        
        GET /api/exam-results/classroom-scores/?exam_id=1&classroom_id=1&subject_id=1
        """
        exam_id = request.query_params.get('exam_id')
        classroom_id = request.query_params.get('classroom_id')
        subject_id = request.query_params.get('subject_id')
        
        if not all([exam_id, classroom_id, subject_id]):
            return Response(
                {'error': 'exam_id, classroom_id, and subject_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if request.user.role != 'teacher':
                return Response(
                    {'error': 'Only teachers can view classroom score entry'},
                    status=status.HTTP_403_FORBIDDEN
                )

            teacher = getattr(request.user, 'teacher_profile', None)
            if not teacher:
                return Response(
                    {'error': 'Teacher profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            exam = Exam.objects.get(id=exam_id, school=request.user.school)
            Classroom.objects.get(id=classroom_id, school=request.user.school)
            Subject.objects.get(id=subject_id, school=request.user.school)
            
            # Verify teacher teaches this subject
            has_permission = TeacherSubject.objects.filter(
                teacher=teacher,
                subject_id=subject_id,
                classroom_id=classroom_id
            ).exists()
            
            if not has_permission:
                return Response(
                    {'error': 'You do not teach this subject in this classroom'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get all results for this exam/classroom/subject
            results = ExamResult.objects.filter(
                exam=exam,
                student__classroom_id=classroom_id,
                subject_id=subject_id
            ).select_related('student', 'exam', 'subject').order_by('student__user__first_name')
            
            serializer = ExamResultSerializer(results, many=True)
            return Response({
                'count': results.count(),
                'results': serializer.data
            })
        
        except Exam.DoesNotExist:
            return Response(
                {'error': 'Exam not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Unable to load classroom scores right now.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AcademicYearViewSet(viewsets.ModelViewSet):
    """ViewSet for managing academic years - supports multi-year records"""
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return AcademicYear.objects.select_related('school').prefetch_related('terms').order_by('-year')
        elif user.school:
            return AcademicYear.objects.filter(
                school=user.school
            ).prefetch_related('terms').order_by('-year')
        return AcademicYear.objects.none()

    def perform_create(self, serializer):
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()


class TermViewSet(viewsets.ModelViewSet):
    """ViewSet for managing terms (semesters/quarters) - supports flexible calendar structures"""
    serializer_class = TermSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Term.objects.select_related('academic_year').order_by('academic_year', 'start_date')
        elif user.school:
            return Term.objects.filter(
                academic_year__school=user.school
            ).select_related('academic_year').order_by('academic_year', 'start_date')
        return Term.objects.none()
