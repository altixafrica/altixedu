from django.contrib import admin
from .models import Announcement, AIRiskAlert


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'target_role', 'is_pinned', 'created_at')
    list_filter = ('school', 'target_role', 'is_pinned', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Announcement', {'fields': ('school', 'title', 'message')}),
        ('Settings', {'fields': ('target_role', 'is_pinned', 'created_by')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AIRiskAlert)
class AIRiskAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'school', 'student', 'alert_type', 'severity', 'is_resolved', 'created_at')
    list_filter = ('school', 'alert_type', 'severity', 'is_resolved', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'message')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Alert Info', {'fields': ('school', 'student', 'alert_type', 'severity')}),
        ('Details', {'fields': ('message', 'recommendation')}),
        ('Status', {'fields': ('is_resolved',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
