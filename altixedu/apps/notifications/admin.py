from django.contrib import admin
from .models import Message, StudentAIInsights, SchoolSetting, RoleSetting


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'read', 'sent_at', 'school')
    list_filter = ('read', 'sent_at', 'school', 'sender__role', 'receiver__role')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('sent_at', 'sender')
    ordering = ('-sent_at',)
    
    fieldsets = (
        ('Participants', {
            'fields': ('sender', 'receiver', 'school')
        }),
        ('Message Content', {
            'fields': ('content', 'student')
        }),
        ('Status', {
            'fields': ('read', 'sent_at')
        }),
    )


@admin.register(StudentAIInsights)
class StudentAIInsightsAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'school',
        'attendance_risk',
        'performance_risk',
        'low_attendance',
        'low_performance'
    )
    list_filter = (
        'school',
        'low_attendance',
        'low_performance',
        'calculated_at'
    )
    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__admission_number'
    )
    readonly_fields = ('calculated_at', 'created_at')
    ordering = ('-performance_risk',)
    
    fieldsets = (
        ('Student', {
            'fields': ('student', 'school')
        }),
        ('Risk Scores', {
            'fields': ('attendance_risk', 'performance_risk')
        }),
        ('Flags', {
            'fields': ('low_attendance', 'low_performance', 'flagged_subjects')
        }),
        ('Metadata', {
            'fields': ('calculated_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SchoolSetting)
class SchoolSettingAdmin(admin.ModelAdmin):
    list_display = ('school', 'school_year', 'attendance_threshold', 'enable_parent_portal')
    list_filter = ('enable_parent_portal', 'enable_student_portal', 'enable_teacher_portal')
    search_fields = ('school__name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('School', {
            'fields': ('school',)
        }),
        ('Branding', {
            'fields': ('logo_url', 'primary_color', 'secondary_color')
        }),
        ('Academic Settings', {
            'fields': (
                'school_year',
                'attendance_threshold',
                'performance_threshold'
            )
        }),
        ('Portal Configuration', {
            'fields': (
                'enable_parent_portal',
                'enable_student_portal',
                'enable_teacher_portal'
            )
        }),
        ('Notifications', {
            'fields': (
                'notification_email',
                'enable_email_alerts',
                'enable_sms_alerts'
            )
        }),
        ('Fee Configuration', {
            'fields': ('default_fee_structure',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RoleSetting)
class RoleSettingAdmin(admin.ModelAdmin):
    list_display = ('role', 'school', 'key', 'updated_at')
    list_filter = ('role', 'school', 'created_at')
    search_fields = ('key', 'role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('role', 'key')
    
    fieldsets = (
        ('Role & School', {
            'fields': ('role', 'school')
        }),
        ('Setting', {
            'fields': ('key', 'value')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
