from rest_framework import viewsets, permissions
from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Attendance.objects.select_related('student', 'recorded_by', 'school').order_by(
                '-date', 'student__last_name', 'student__first_name'
            )
        elif user.school:
            return Attendance.objects.filter(school=user.school).select_related(
                'student', 'recorded_by', 'school'
            ).order_by('-date', 'student__last_name', 'student__first_name')
        return Attendance.objects.none()

    def perform_create(self, serializer):
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()
