from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'school', 'employment_date', 'status')
    list_filter = ('school', 'status', 'employment_date')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'school')}),
        ('Employment', {'fields': ('employment_date', 'status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
