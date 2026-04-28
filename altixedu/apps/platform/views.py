"""
Views for platform endpoints (school branding, announcements, setup).
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.accounts.models import User
from apps.schools.models import School
from apps.students.models import Student
from apps.platform.models import Announcement, AIRiskAlert
from apps.platform.serializers import (
    SchoolBrandingSerializer, SchoolUpdateSerializer,
    AnnouncementSerializer, AIRiskAlertSerializer,
    SubdomainCheckSerializer, SchoolRegistrationSerializer
)
from apps.billing.provisioning import seed_school_subscription
from platform_service import (
    SubdomainValidator, SchoolProvisioner, BrandingService
)


def get_request_school_id(request):
    """
    Resolve school context from subdomain middleware first, then the authenticated user.

    The Next.js frontend currently talks to Django through a single API base URL, so
    subdomain-derived tenant context is not always present. For authenticated school users,
    falling back to request.user.school_id keeps school-scoped endpoints usable and avoids
    accidentally treating ordinary users as superadmins.
    """
    school_id = getattr(request, 'school_id', None)
    if school_id:
        return school_id

    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        return getattr(user, 'school_id', None)

    return None


ROLE_AUDIENCE_MAP = {
    'admin': 'admin',
    'teacher': 'teachers',
    'parent': 'parents',
    'student': 'students',
    'bursar': 'all',
    'superadmin': 'all',
    'ministry_admin': 'all',
}


class PlatformOverviewAPIView(APIView):
    """
    Public platform overview used by the landing page and partner pages.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        active_schools = School.objects.filter(is_active=True)
        countries = list(
            active_schools.exclude(country='')
            .values_list('country', flat=True)
            .distinct()
            .order_by('country')
        )
        languages = list(
            active_schools.exclude(language='')
            .values_list('language', flat=True)
            .distinct()
            .order_by('language')
        )
        school_types = active_schools.values('school_type').annotate(
            count=Count('id')
        ).order_by('-count', 'school_type')

        return Response({
            'service': 'AltixEdu',
            'generated_at': timezone.now(),
            'metrics': {
                'active_schools': active_schools.count(),
                'students_managed': Student.objects.filter(
                    school__is_active=True
                ).count(),
                'staff_accounts': User.objects.filter(
                    school__is_active=True,
                    role__in=['admin', 'teacher', 'bursar', 'parent']
                ).count(),
                'countries': len(countries),
            },
            'coverage': {
                'countries': countries,
                'languages': languages,
                'school_types': [
                    {
                        'type': item['school_type'],
                        'count': item['count'],
                    }
                    for item in school_types
                ],
            },
            'product_focus': [
                'Private school operations',
                'Public school administration',
                'Ministry and state oversight',
                'Multi-school finance oversight and reporting',
            ],
        }, status=status.HTTP_200_OK)


class PlatformHealthAPIView(APIView):
    """
    Lightweight health endpoint for probes and uptime checks.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        database_status = 'ok'
        response_status = status.HTTP_200_OK

        try:
            School.objects.exists()
        except Exception:
            database_status = 'error'
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE

        return Response({
            'status': 'ok' if database_status == 'ok' else 'degraded',
            'database': database_status,
            'service': 'altixedu-platform',
            'time': timezone.now(),
        }, status=response_status)


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
        school_id = get_request_school_id(request)
        if school_id:
            branding = BrandingService.get_branding(school_id)
            if branding:
                serializer = SchoolBrandingSerializer(
                    School.objects.get(id=school_id),
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
        school_id = get_request_school_id(request)
        if not school_id:
            return Response(
                {'error': 'Cannot update superadmin branding'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        school = School.objects.get(id=school_id)
        serializer = SchoolBrandingSerializer(
            school,
            context={'request': request}
        )
        return Response(serializer.data)
    
    def put(self, request):
        """Update school branding."""
        return self._update_school_branding(request)

    def patch(self, request):
        """Partially update school branding."""
        return self._update_school_branding(request)

    def _update_school_branding(self, request):
        """Update school branding."""
        school_id = get_request_school_id(request)
        if not school_id:
            return Response(
                {'error': 'Cannot update superadmin branding'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is admin of this school
        if request.user.school_id != school_id:
            return Response(
                {'error': 'Not authorized to update this school'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        school = School.objects.get(id=school_id)
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
            subscription = seed_school_subscription(school)
            
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
                'subscription': {
                    'tier': subscription.tier.display_name if subscription and subscription.tier else None,
                    'status': subscription.status if subscription else None,
                } if subscription else None,
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
        school_id = get_request_school_id(self.request)
        user = self.request.user

        if user.role == 'superadmin' and not school_id:
            return Announcement.objects.all()

        if not school_id:
            return Announcement.objects.none()
        
        # Regular users see announcements for their school
        # and announcements targeting their role or "all"
        queryset = Announcement.objects.select_related('created_by', 'school').filter(
            school_id=school_id
        )

        if user.role == 'admin':
            return queryset.order_by('-is_pinned', '-created_at')
        
        # Filter by role if applicable
        user_role = ROLE_AUDIENCE_MAP.get(user.role, user.role)
        queryset = queryset.filter(
            Q(target_role='all') | Q(target_role=user_role)
        )
        
        return queryset.order_by('-is_pinned', '-created_at')

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only school admins can create announcements'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not get_request_school_id(request):
            return Response(
                {'error': 'School context is required to create announcements'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        announcement = self.get_object()
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only school admins can update announcements'},
                status=status.HTTP_403_FORBIDDEN
            )
        if request.user.role != 'superadmin' and request.user.school_id != announcement.school_id:
            return Response(
                {'error': 'You can only update announcements in your school'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        announcement = self.get_object()
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only school admins can delete announcements'},
                status=status.HTTP_403_FORBIDDEN
            )
        if request.user.role != 'superadmin' and request.user.school_id != announcement.school_id:
            return Response(
                {'error': 'You can only delete announcements in your school'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set creator and school."""
        school_id = get_request_school_id(self.request)
        serializer.save(
            created_by=self.request.user,
            school_id=school_id
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
        school_id = get_request_school_id(self.request)
        user = self.request.user

        if user.role == 'superadmin' and not school_id:
            return AIRiskAlert.objects.all()

        if not school_id:
            return AIRiskAlert.objects.none()
        
        queryset = AIRiskAlert.objects.filter(school_id=school_id)
        
        # Students only see alerts for themselves
        if user.role == 'student':
            try:
                student = user.student_profile
                queryset = queryset.filter(student=student)
            except:
                queryset = queryset.none()
        
        # Parents see alerts for their children
        elif user.role == 'parent':
            try:
                parent = user.parent_profile
                child_ids = parent.children.values_list('id', flat=True)
                queryset = queryset.filter(student_id__in=child_ids)
            except:
                queryset = queryset.none()
        
        # Teachers can see alerts but are read-only
        # Admins can see all
        
        return queryset.order_by('-severity', '-created_at')
