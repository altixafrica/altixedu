from django.db import models
from django.utils import timezone


class ActiveSchoolManager(models.Manager):
    """Manager that only returns active (non-deleted) schools"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, deleted_at__isnull=True)


class AllSchoolManager(models.Manager):
    """Manager that returns all schools, including deleted ones"""
    def get_queryset(self):
        return super().get_queryset()


class Ministry(models.Model):
    """
    Government ministry/education authority entity for regional-level dashboard aggregation.
    Used for centralized reporting in African countries.
    """
    # Regional/Provincial structure
    name = models.CharField(
        max_length=255,
        help_text="Name of the ministry (e.g., Ministry of Education)"
    )
    country = models.CharField(
        max_length=100,
        help_text="Country (e.g., Nigeria, Kenya, Ghana, South Africa)"
    )
    state_or_province = models.CharField(
        max_length=100,
        help_text="State/Province/Region name (e.g., Lagos, Nairobi, Accra)"
    )
    state = models.CharField(
        max_length=100,
        unique=False,  # Not unique because same state names exist in different countries
        help_text="Legacy field - use state_or_province instead"
    )
    
    # Contact & Location
    contact_email = models.EmailField(help_text="Ministry contact email")
    contact_phone = models.CharField(max_length=20, help_text="Ministry contact phone")
    address = models.TextField(help_text="Ministry office address")
    
    # Currency configuration
    currency_code = models.CharField(
        max_length=3,
        default="NGN",
        help_text="ISO 4217 currency code (NGN for Nigeria, KES for Kenya, GHS for Ghana, etc.)"
    )
    currency_symbol = models.CharField(
        max_length=5,
        default="₦",
        help_text="Currency symbol (₦ for Naira, KES for Kenyan Shilling, etc.)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Ministries"
        ordering = ['country', 'state_or_province']
        unique_together = [['country', 'state_or_province']]  # Unique per country

    def __str__(self):
        return f"{self.name} ({self.state_or_province}, {self.country})"


class School(models.Model):
    SCHOOL_TYPE_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('charter', 'Charter'),
    )
    
    name = models.CharField(max_length=255)
    subdomain = models.CharField(
        max_length=100,
        unique=True,
        help_text="Subdomain for accessing school (e.g., 'muse' for muse.altixedu.com)"
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    logo = models.ImageField(
        upload_to='school_logos/',
        null=True,
        blank=True,
        help_text="School logo image"
    )
    primary_color = models.CharField(
        max_length=7,
        default="#0066CC",
        help_text="Primary color in hex format"
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#FF6600",
        help_text="Secondary color in hex format"
    )
    timezone = models.CharField(
        max_length=100,
        default="UTC",
        help_text="e.g., Africa/Lagos, America/New_York"
    )
    language = models.CharField(
        max_length=10,
        default="en",
        help_text="Default language for school"
    )
    # Multi-currency support for African schools
    currency_code = models.CharField(
        max_length=3,
        default="USD",
        help_text="ISO 4217 currency code (KES, UGX, NGN, GHS, ZAR, TZS, ETB, etc.)"
    )
    currency_symbol = models.CharField(
        max_length=10,
        default="$",
        help_text="Currency symbol (e.g., ₦, KES, UGX)"
    )
    # Academic calendar format
    academic_year_format = models.CharField(
        max_length=20,
        choices=[
            ('calendar', 'Calendar Year (Jan-Dec)'),
            ('african_sep', 'African Year (Sep-Aug)'),
            ('african_jan', 'Academic Year (Jan-Dec after sep-aug)'),
            ('custom', 'Custom Dates'),
        ],
        default='african_sep',
        help_text="School calendar format (most African schools: Sep-Aug)"
    )
    school_type = models.CharField(
        max_length=20,
        choices=SCHOOL_TYPE_CHOICES,
        default='private'
    )
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Geographic region for default templates"
    )
    ministry = models.ForeignKey(
        Ministry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schools',
        help_text="Ministry that provisioned or governs this school"
    )
    established_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Superadmin can suspend schools"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Soft-delete timestamp (NULL = not deleted)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom managers
    objects = ActiveSchoolManager()  # Default manager - only active schools
    all_objects = AllSchoolManager()  # Manager for all schools including deleted

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['is_active']),
            models.Index(fields=['deleted_at']),
            models.Index(fields=['is_active', 'deleted_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.subdomain})"
    
    @property
    def full_domain(self):
        """Return the full domain URL for this school"""
        return f"{self.subdomain}.altixedu.com"
    
    def soft_delete(self):
        """Soft delete the school (mark as deleted without removing data)"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore a soft-deleted school"""
        self.is_active = True
        self.deleted_at = None
        self.save()
