"""
Platform service module for school operations.

Provides:
- Subdomain validation and generation
- School provisioning
- Branding utilities
"""
import re
import string
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.schools.models import School
from apps.accounts.models import User


class SubdomainValidator:
    """Validate and generate subdomains for schools."""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    PATTERN = re.compile(r'^[a-z0-9-]+$')
    RESERVED = {
        'api', 'admin', 'www', 'localhost', 'staging', 'production',
        'development', 'test', 'sandbox', 'demo', 'help', 'support',
        'mail', 'ftp', 'smtp', 'imap', 'pop', 'webmail', 'upload',
        'download', 'static', 'media', 'cdn', 'assets',
    }
    
    @classmethod
    def validate(cls, subdomain):
        """
        Validate subdomain format.
        
        Rules:
        - 3-50 characters
        - lowercase letters, numbers, hyphens only
        - cannot start or end with hyphen
        - not in reserved list
        - must be unique (not already taken)
        
        Returns None if valid, raises ValidationError if invalid.
        """
        if not subdomain:
            raise ValidationError("Subdomain is required")
        
        subdomain = subdomain.lower().strip()
        
        # Check length
        if len(subdomain) < cls.MIN_LENGTH:
            raise ValidationError(
                f"Subdomain must be at least {cls.MIN_LENGTH} characters"
            )
        if len(subdomain) > cls.MAX_LENGTH:
            raise ValidationError(
                f"Subdomain cannot exceed {cls.MAX_LENGTH} characters"
            )
        
        # Check format
        if not cls.PATTERN.match(subdomain):
            raise ValidationError(
                "Subdomain can only contain lowercase letters, numbers, and hyphens"
            )
        
        # Check start/end characters
        if subdomain.startswith('-') or subdomain.endswith('-'):
            raise ValidationError("Subdomain cannot start or end with hyphen")
        
        # Check reserved words
        if subdomain in cls.RESERVED:
            raise ValidationError(
                f"Subdomain '{subdomain}' is reserved. Choose another."
            )
        
        # Check uniqueness
        if School.objects.filter(subdomain=subdomain).exists():
            raise ValidationError(
                f"Subdomain '{subdomain}' is already taken. Choose another."
            )
        
        return True
    
    @classmethod
    def is_available(cls, subdomain):
        """Check if subdomain is available (doesn't raise exception)."""
        try:
            cls.validate(subdomain)
            return True
        except ValidationError:
            return False
    
    @classmethod
    def suggest_subdomains(cls, school_name):
        """
        Generate subdomain suggestions from school name.
        
        Examples:
        - 'Muse Academy' -> ['muse', 'muse-academy', 'muse-school']
        - 'St. John High School' -> ['st-john', 'st-john-high', 'stjohn']
        """
        suggestions = []
        
        # Clean school name
        name = school_name.lower().strip()
        name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars
        name = re.sub(r'\s+', '-', name)  # Replace spaces with hyphens
        name = re.sub(r'-+', '-', name)  # Remove double hyphens
        
        # Get first words
        words = name.split('-')
        
        # Suggestion 1: first word
        if words:
            base = words[0]
            if cls.is_available(base):
                suggestions.append(base)
        
        # Suggestion 2: first two words
        if len(words) >= 2:
            two_words = '-'.join(words[:2])
            if len(two_words) <= cls.MAX_LENGTH and cls.is_available(two_words):
                suggestions.append(two_words)
        
        # Suggestion 3: first three words
        if len(words) >= 3:
            three_words = '-'.join(words[:3])
            if len(three_words) <= cls.MAX_LENGTH and cls.is_available(three_words):
                suggestions.append(three_words)
        
        # Suggestion 4: all words (if available and not too long)
        if len(words) > 3:
            all_words = '-'.join(words[:4])
            if len(all_words) <= cls.MAX_LENGTH and cls.is_available(all_words):
                suggestions.append(all_words)
        
        # Suggestion 5: first word + number (if first word taken)
        if words and not cls.is_available(words[0]):
            for i in range(1, 10):
                numbered = f"{words[0]}{i}"
                if cls.is_available(numbered):
                    suggestions.append(numbered)
                    break
        
        return suggestions


class SchoolProvisioner:
    """Provision new schools with default settings."""

    @staticmethod
    def _generate_username(email):
        base_username = re.sub(r'[^a-z0-9._-]', '', email.split('@')[0].lower())
        base_username = base_username or 'schooladmin'
        candidate = base_username[:150]
        counter = 1

        while User.objects.filter(username=candidate).exists():
            suffix = f'-{counter}'
            candidate = f"{base_username[:150 - len(suffix)]}{suffix}"
            counter += 1

        return candidate
    
    @transaction.atomic
    def create_school(self, name, subdomain, email, admin_email, admin_password,
                      phone='', city='', state='', country='', **kwargs):
        """
        Create a new school and admin user.
        
        Args:
            name: School name
            subdomain: School subdomain (must be validated first)
            email: School contact email
            admin_email: Admin user email
            admin_password: Admin user password
            phone: School phone
            city: School city
            state: School state
            country: School country
            **kwargs: Additional School fields (timezone, language, region, etc.)
        
        Returns:
            Tuple of (school, user) objects
        """
        # Validate subdomain one more time
        try:
            SubdomainValidator.validate(subdomain)
        except ValidationError as e:
            raise ValueError(f"Invalid subdomain: {e.message}") from e
        
        admin_first_name = kwargs.pop('admin_first_name', 'Admin')
        admin_last_name = kwargs.pop('admin_last_name', 'User')
        school_fields = {
            key: value
            for key, value in kwargs.items()
            if key in {
                'address',
                'postal_code',
                'website',
                'primary_color',
                'secondary_color',
                'timezone',
                'language',
                'school_type',
                'region',
                'established_year',
            }
        }

        # Create school
        school = School.objects.create(
            name=name,
            subdomain=subdomain,
            email=email,
            phone=phone,
            address=school_fields.pop('address', ''),  # Can be completed during onboarding
            city=city,
            state=state,
            country=country,
            is_active=True,
            **school_fields
        )
        
        # Create admin user
        user = User.objects.create_user(
            username=self._generate_username(admin_email),
            email=admin_email,
            password=admin_password,
            first_name=admin_first_name,
            last_name=admin_last_name,
            role='admin',
            school=school,
            is_active=True
        )
        
        return school, user
    
    @staticmethod
    def suspend_school(school_id):
        """Suspend a school (superadmin only)."""
        school = School.objects.get(id=school_id)
        school.is_active = False
        school.save()
        return school
    
    @staticmethod
    def activate_school(school_id):
        """Activate a suspended school (superadmin only)."""
        school = School.objects.get(id=school_id)
        school.is_active = True
        school.save()
        return school


class BrandingService:
    """Manage school branding and customization."""
    
    @staticmethod
    def get_branding(school_id):
        """
        Get school branding information.
        
        Returns:
            Dict with: name, logo, primary_color, secondary_color, 
                      language, timezone, full_domain
        """
        try:
            school = School.objects.get(id=school_id, is_active=True)
            return {
                'id': school.id,
                'name': school.name,
                'subdomain': school.subdomain,
                'full_domain': school.full_domain,
                'logo': school.logo.url if school.logo else None,
                'primary_color': school.primary_color,
                'secondary_color': school.secondary_color,
                'language': school.language,
                'timezone': school.timezone,
                'website': school.website,
            }
        except School.DoesNotExist:
            return None
    
    @staticmethod
    def get_branding_by_subdomain(subdomain):
        """Get branding by subdomain (for frontend)."""
        try:
            school = School.objects.get(subdomain=subdomain, is_active=True)
            return BrandingService.get_branding(school.id)
        except School.DoesNotExist:
            return None
    
    @staticmethod
    def update_branding(school_id, **fields):
        """
        Update school branding.
        
        Allowed fields: primary_color, secondary_color, logo, 
                       language, timezone, website
        """
        school = School.objects.get(id=school_id)
        
        allowed_fields = {
            'primary_color', 'secondary_color', 'logo',
            'language', 'timezone', 'website'
        }
        
        for field, value in fields.items():
            if field in allowed_fields:
                setattr(school, field, value)
        
        school.save()
        return school
