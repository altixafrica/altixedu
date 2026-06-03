from django.contrib import admin
from .models import AnalyticsDashboard, SchoolPerformanceMetric


@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ['school', 'total_students', 'students_at_risk_count', 'collection_rate_percentage', 'calculated_at']
    list_filter = ['school', 'calculated_at']
    readonly_fields = ['calculated_at', 'created_at']


@admin.register(SchoolPerformanceMetric)
class SchoolPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['school', 'date', 'attendance_rate', 'average_score', 'fees_collected_today']
    list_filter = ['school', 'date']
    date_hierarchy = 'date'
