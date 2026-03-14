"""
Multi-Language Support (i18n) for AltixEdu
Support for Spanish, French, and local languages
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.schools.models import School


class SupportedLanguage(models.Model):
    """Define supported languages for the system"""
    
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Language code (e.g., 'en', 'es', 'fr')"
    )
    name = models.CharField(
        max_length=50,
        help_text="Language name in English (e.g., 'English', 'Spanish')"
    )
    name_native = models.CharField(
        max_length=50,
        help_text="Language name in native language (e.g., 'Español')"
    )
    
    is_active = models.BooleanField(default=True)
    
    # Settings
    flag_emoji = models.CharField(
        max_length=10,
        blank=True,
        help_text="Flag emoji for the language"
    )
    
    is_rtl = models.BooleanField(
        default=False,
        help_text="Right-to-left language (for Arabic, Hebrew, etc.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class UserLanguagePreference(models.Model):
    """Store user's preferred language"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='language_preference'
    )
    
    preferred_language = models.ForeignKey(
        SupportedLanguage,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        help_text="User's preferred language"
    )
    
    # Alternative languages (for reference)
    secondary_languages = models.ManyToManyField(
        SupportedLanguage,
        blank=True,
        related_name='secondary_users',
        help_text="Secondary languages the user understands"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        lang_name = self.preferred_language.name if self.preferred_language else "Not Set"
        return f"{self.user.get_full_name()} - {lang_name}"


class TranslationResource(models.Model):
    """Store translations for various UI elements and content"""
    
    RESOURCE_TYPES = (
        ('dashboard', 'Dashboard'),
        ('form', 'Form'),
        ('email', 'Email'),
        ('notification', 'Notification'),
        ('report', 'Report'),
        ('menu', 'Menu'),
        ('message', 'Message'),
        ('error', 'Error'),
    )
    
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    resource_key = models.CharField(
        max_length=255,
        help_text="Unique key for this resource (e.g., 'dashboard.welcome')"
    )
    
    # Default English version
    english_text = models.TextField(
        help_text="Default English text"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Context/description for translators"
    )
    
    # Translations (stored as JSON)
    translations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dictionary of language_code: translated_text"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('resource_type', 'resource_key')
        ordering = ['resource_type', 'resource_key']
        indexes = [
            models.Index(fields=['resource_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.resource_type}: {self.resource_key}"
    
    def get_text_for_language(self, language_code):
        """Get translated text for a specific language"""
        if language_code in self.translations:
            return self.translations[language_code]
        return self.english_text


class SchoolLanguageSettings(models.Model):
    """School-specific language settings"""
    
    school = models.OneToOneField(
        School,
        on_delete=models.CASCADE,
        related_name='language_settings'
    )
    
    # Default language for school
    default_language = models.ForeignKey(
        SupportedLanguage,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Default language for this school"
    )
    
    # Enabled languages
    enabled_languages = models.ManyToManyField(
        SupportedLanguage,
        related_name='schools',
        help_text="Languages available in this school"
    )
    
    # Locale-specific settings
    date_format = models.CharField(
        max_length=20,
        default='YYYY-MM-DD',
        help_text="Date format (e.g., DD/MM/YYYY, MM/DD/YYYY)"
    )
    
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code (USD, EUR, GBP, etc.)"
    )
    
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="Timezone for the school"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.school.name} - Language Settings"


def get_translation(resource_key, language_code='en', default=None):
    """
    Simple utility to get a translation.
    
    Args:
        resource_key: Key of the resource (e.g., 'dashboard.welcome')
        language_code: Language code (e.g., 'es', 'fr')
        default: Default value if translation not found
    
    Returns:
        Translated text or default
    """
    try:
        parts = resource_key.split('.')
        resource_type = parts[0] if parts else 'message'
        key = '.'.join(parts) if len(parts) > 1 else resource_key
        
        translation = TranslationResource.objects.get(
            resource_type=resource_type,
            resource_key=key,
            is_active=True
        )
        
        return translation.get_text_for_language(language_code)
    
    except TranslationResource.DoesNotExist:
        return default or resource_key
