"""
Views for platform endpoints (school branding, announcements, setup).
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from apps.schools.models import School
from apps.platform.models import Announcement, AIRiskAlert
from apps.platform.serializers import (
    SchoolBrandingSerializer, SchoolUpdateSerializer,
    AnnouncementSerializer, AIRiskAlertSerializer,
    SubdomainCheckSerializer, SchoolRegistrationSerializer
)
from platform_service import (
    SubdomainValidator, SchoolProvisioner, BrandingService
)


class BrandingPublicAPIView(APIView):
    """
    Public API endpoint for school branding.
    
    GET /api/platform/branding/
    - Returns branding for current school (via subdomain middleware)
    - No authentication required
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get branding for current school."""
        if request.school_id:
            branding = BrandingService.get_branding(request.school_id)
            if branding:
                serializer = SchoolBrandingSerializer(
                    School.objects.get(id=request.school_id),
                    context={'request': request}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'School not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class BrandingAdminAPIView(APIView):
    """
    Admin API endpoint for updating school branding.
    
    GET /api/platform/branding-admin/
    - Returns current branding
    
    PUT /api/platform/branding-admin/
    - Updates school branding (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current school branding."""
        if not request.school_id:
            return Response(
                {'error': 'Cannot update superadmin branding'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        school = School.objects.get(id=request.school_id)
        serializer = SchoolBrandingSerializer(
            school,
            context={'request': request}
        )
        return Response(serializer.data)
    
    def put(self, request):
        """Update school branding."""
        if not request.school_id:
            return Response(
                {'error': 'Cannot update superadmin branding'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is admin of this school
        if request.user.school_id != request.school_id:
            return Response(
                {'error': 'Not authorized to update this school'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        school = School.objects.get(id=request.school_id)
        serializer = SchoolUpdateSerializer(
            school,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubdomainCheckAPIView(APIView):
    """
    Check subdomain availability and suggestions.
    
    POST /api/platform/check-subdomain/
    {
        "subdomain": "muse",
        "school_name": "Muse Academy"  // optional, for suggestions
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Check if subdomain is available."""
        subdomain = request.data.get('subdomain', '').strip()
        school_name = request.data.get('school_name', '')
        
        if not subdomain:
            return Response(
                {'error': 'Subdomain is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check availability
        is_available = SubdomainValidator.is_available(subdomain)
        
        response_data = {
            'subdomain': subdomain,
            'is_available': is_available,
        }
        
        # If not available but school_name provided, suggest alternatives
        if not is_available and school_name:
            suggestions = SubdomainValidator.suggest_subdomains(school_name)
            response_data['suggestions'] = suggestions
            response_data['message'] = (
                f"Subdomain '{subdomain}' is not available. "
                "Try one of the suggestions."
            )
        elif is_available:
            response_data['message'] = f"Subdomain '{subdomain}' is available!"
        else:
            response_data['message'] = f"Subdomain '{subdomain}' is not available"
        
        return Response(response_data)


class SchoolRegistrationAPIView(APIView):
    """
    Register a new school.
    
    POST /api/platform/register-school/
    {
        "name": "Muse Academy",
        "subdomain": "muse",
        "email": "school@muse.edu",
        "phone": "+234800000000",
        "city": "Lagos",
        "country": "Nigeria",
        "admin_email": "admin@muse.edu",
        "admin_password": "SecurePass123!",
        "admin_first_name": "John",
        "admin_last_name": "Doe",
        "timezone": "Africa/Lagos",
        "language": "en",
        "region": "West Africa"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Register a new school."""
        serializer = SchoolRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        try:
            # Validate subdomain
            SubdomainValidator.validate(data['subdomain'])
        except DjangoValidationError as e:
            return Response(
                {'subdomain': [str(e.message)]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create school and admin user
            provisioner = SchoolProvisioner()
            school, user = provisioner.create_school(
                name=data['name'],
                subdomain=data['subdomain'],
                email=data['email'],
                phone=data.get('phone', ''),
                city=data.get('city', ''),
                state=data.get('state', ''),
                country=data.get('country', 'Nigeria'),
                admin_email=data['admin_email'],
                admin_password=data['admin_password'],
                admin_first_name=data['admin_first_name'],
                admin_last_name=data['admin_last_name'],
                timezone=data.get('timezone', 'UTC'),
                language=data.get('language', 'en'),
                region=data.get('region', ''),
                school_type=data.get('school_type', 'private'),
            )
            
            response_data = {
                'message': 'School registered successfully!',
                'school': {
                    'id': school.id,
                    'name': school.name,
                    'subdomain': school.subdomain,
                    'full_domain': school.full_domain,
                    'email': school.email,
                },
                'admin_user': {
                    'email': user.email,
                    'full_name': user.get_full_name(),
                },
                'next_steps': [
                    'Login at ' + school.full_domain,
                    'Complete school setup wizard',
                    'Add classrooms and subjects',
                    'Invite teachers and students'
                ]
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to create school: ' + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for announcements.
    
    - List: GET /api/platform/announcements/
    - Create: POST /api/platform/announcements/
    - Retrieve: GET /api/platform/announcements/{id}/
    - Update: PUT /api/platform/announcements/{id}/
    - Delete: DELETE /api/platform/announcements/{id}/
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter announcements by school and target role."""
        if not self.request.school_id:
            # Superadmin can see all
            return Announcement.objects.all()
        
        # Regular users see announcements for their school
        # and announcements targeting their role or "all"
        queryset = Announcement.objects.filter(
            school_id=self.request.school_id
        )
        
        # Filter by role if applicable
        user_role = self.request.user.role
        queryset = queryset.filter(
            Q(target_role='all') | Q(target_role=user_role)
        )
        
        return queryset.order_by('-is_pinned', '-created_at')
    
    def perform_create(self, serializer):
        """Set creator and school."""
        serializer.save(
            created_by=self.request.user,
            school_id=self.request.school_id
        )


class AIRiskAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AI risk alerts (read-only for non-staff).
    
    - List: GET /api/platform/ai-risk-alerts/
    - Retrieve: GET /api/platform/ai-risk-alerts/{id}/
    """
    serializer_class = AIRiskAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter alerts by school and visibility."""
        if not self.request.school_id:
            # Superadmin sees all
            return AIRiskAlert.objects.all()
        
        queryset = AIRiskAlert.objects.filter(school_id=self.request.school_id)
        
        # Students only see alerts for themselves
        if self.request.user.role == 'student':
            try:
                student = self.request.user.student_profile
                queryset = queryset.filter(student=student)
            except:
                queryset = queryset.none()
        
        # Parents see alerts for their children
        elif self.request.user.role == 'parent':
            try:
                parent = self.request.user.parent_profile
                child_ids = parent.children.values_list('id', flat=True)
                queryset = queryset.filter(student_id__in=child_ids)
            except:
                queryset = queryset.none()
        
        # Teachers can see alerts but are read-only
        # Admins can see all
        
        return queryset.order_by('-severity', '-created_at')
