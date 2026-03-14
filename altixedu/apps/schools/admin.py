from django.contrib import admin
from .models import School, Ministry


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain', 'full_domain', 'email', 'is_active', 'school_type', 'created_at')
    list_filter = ('is_active', 'school_type', 'region', 'created_at')
    search_fields = ('name', 'email', 'subdomain')
    readonly_fields = ('created_at', 'updated_at', 'full_domain')
    
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'email', 'phone')}),
        ('Subdomain', {
            'fields': ('subdomain', 'full_domain', 'is_active'),
            'description': 'Configure subdomain (e.g., "muse" for muse.altixedu.com) and manage school access'
        }),
        ('Address', {'fields': ('address', 'city', 'postal_code', 'state', 'country')}),
        ('Organization', {'fields': ('school_type', 'region', 'established_year', 'website')}),
        ('Branding', {'fields': ('logo', 'primary_color', 'secondary_color')}),
        ('Settings', {'fields': ('timezone', 'language')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'contact_email')
