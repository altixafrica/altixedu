from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.teachers.models import Teacher
from apps.teachers.serializers import TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing teachers.
    
    list: Get all teachers for the current school
    retrieve: Get a specific teacher
    create: Create a new teacher
    update: Update teacher information
    destroy: Delete a teacher
    """
    
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter teachers by current user's school"""
        user = self.request.user
        if hasattr(user, 'school'):
            return Teacher.objects.filter(school=user.school)
        return Teacher.objects.none()
    
    def perform_create(self, serializer):
        """Set school from user's school when creating"""
        user = self.request.user
        if hasattr(user, 'school'):
            serializer.save(school=user.school)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active teachers"""
        teachers = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(teachers, many=True)
        return Response(serializer.data)
