from rest_framework import viewsets, permissions
from apps.bursars.models import Bursar
from apps.bursars.serializers import BursarSerializer


class BursarViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing bursars (finance managers).
    
    list: Get all bursars for the current school
    retrieve: Get a specific bursar
    create: Create a new bursar
    update: Update bursar information
    destroy: Delete a bursar
    """
    
    queryset = Bursar.objects.all()
    serializer_class = BursarSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter bursars by current user's school"""
        user = self.request.user
        if hasattr(user, 'school'):
            return Bursar.objects.filter(school=user.school)
        return Bursar.objects.none()
    
    def perform_create(self, serializer):
        """Set school from user's school when creating"""
        user = self.request.user
        if hasattr(user, 'school'):
            serializer.save(school=user.school)
        else:
            serializer.save()
