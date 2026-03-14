from rest_framework import viewsets, permissions
from .models import (
    Classroom,
    Subject,
    TeacherSubject,
    Exam,
    ExamResult
)
from .serializers import (
    ClassroomSerializer,
    SubjectSerializer,
    TeacherSubjectSerializer,
    ExamSerializer,
    ExamResultSerializer
)


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Classroom.objects.all()
        elif user.school:
            return Classroom.objects.filter(school=user.school)
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
            return Subject.objects.all()
        elif user.school:
            return Subject.objects.filter(school=user.school)
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
            return TeacherSubject.objects.all()
        elif user.school:
            return TeacherSubject.objects.filter(
                classroom__school=user.school
            )
        return TeacherSubject.objects.none()


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
            return ExamResult.objects.all()
        elif user.school:
            return ExamResult.objects.filter(exam__school=user.school)
        return ExamResult.objects.none()
