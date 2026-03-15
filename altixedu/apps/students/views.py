from rest_framework import viewsets, permissions
from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Student.objects.all()
        elif user.school:
            return Student.objects.filter(school=user.school)
        return Student.objects.none()

    def perform_create(self, serializer):
        # Auto-set school from user's school
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()
