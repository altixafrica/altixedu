"""
Serializers for platform endpoints (announcements, branding, school setup).
"""
from rest_framework import serializers
from apps.schools.models import School
from apps.platform.models import Announcement, AIRiskAlert


class SchoolBrandingSerializer(serializers.ModelSerializer):
    """Serializer for school branding information (public-facing)."""
    full_domain = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'subdomain', 'full_domain', 'logo',
            'logo_url', 'email', 'primary_color', 'secondary_color',
            'language', 'timezone', 'website'
        ]
        read_only_fields = fields
    
    def get_full_domain(self, obj):
        return obj.full_domain
    
    def get_logo(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

    def get_logo_url(self, obj):
        return self.get_logo(obj)


class SchoolUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating school branding (admin-only)."""
    
    class Meta:
        model = School
        fields = [
            'name', 'email', 'primary_color',
            'secondary_color', 'logo', 'language',
            'timezone', 'website'
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    """Serializer for announcements."""
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'school', 'title', 'message', 'target_role',
            'created_by', 'created_by_name', 'is_pinned',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'school',
            'created_by',
            'created_at',
            'updated_at',
            'created_by_name',
        ]


class AIRiskAlertSerializer(serializers.ModelSerializer):
    """Serializer for AI risk alerts."""
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True,
        allow_null=True
    )
    severity_display = serializers.CharField(
        source='get_severity_display',
        read_only=True
    )
    alert_type_display = serializers.CharField(
        source='get_alert_type_display',
        read_only=True
    )
    
    class Meta:
        model = AIRiskAlert
        fields = [
            'id', 'school', 'student', 'student_name',
            'alert_type', 'alert_type_display',
            'severity', 'severity_display',
            'message', 'recommendation', 'is_resolved',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'student_name', 'severity_display',
            'alert_type_display', 'created_at', 'updated_at'
        ]


class SubdomainCheckSerializer(serializers.Serializer):
    """Serializer for checking subdomain availability."""
    subdomain = serializers.CharField(max_length=100)
    is_available = serializers.BooleanField(read_only=True)
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        required=False
    )
    message = serializers.CharField(read_only=True, required=False)


class SchoolRegistrationSerializer(serializers.Serializer):
    """Serializer for school registration."""
    # School info
    name = serializers.CharField(max_length=255)
    subdomain = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, default='Nigeria')
    
    # Admin user info
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'}
    )
    admin_first_name = serializers.CharField(max_length=150)
    admin_last_name = serializers.CharField(max_length=150)
    
    # Optional settings
    timezone = serializers.CharField(max_length=100, required=False, default='UTC')
    language = serializers.CharField(max_length=10, required=False, default='en')
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    school_type = serializers.ChoiceField(
        choices=School.SCHOOL_TYPE_CHOICES,
        required=False,
        default='private'
    )
