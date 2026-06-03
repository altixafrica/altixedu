from django.db import models
from apps.schools.models import School


class AnalyticsDashboard(models.Model):
    """Cached analytics data for fast dashboard loading"""
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='analytics_dashboard')
    
    # Student metrics
    total_students = models.IntegerField(default=0)
    students_at_risk_count = models.IntegerField(default=0)
    average_attendance_rate = models.FloatField(default=0.0)
    average_performance_rate = models.FloatField(default=0.0)
    
    # Finance metrics
    total_fees_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_fees_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    collection_rate_percentage = models.FloatField(default=0.0)
    
    # Teacher metrics
    total_teachers = models.IntegerField(default=0)
    active_classrooms = models.IntegerField(default=0)
    
    # Trends
    enrollment_growth_rate = models.FloatField(default=0.0, help_text="Month-over-month growth %")
    attendance_trend = models.CharField(max_length=10, default='stable', choices=[
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ])
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Analytics Dashboards"

    def __str__(self):
        return f"Analytics: {self.school.name}"


class SchoolPerformanceMetric(models.Model):
    """Daily performance metrics for trend analysis"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='performance_metrics')
    
    date = models.DateField(auto_now_add=True)
    
    # Attendance
    total_present = models.IntegerField(default=0)
    total_absent = models.IntegerField(default=0)
    attendance_rate = models.FloatField(default=0.0)
    
    # Performance
    average_score = models.FloatField(default=0.0)
    students_above_threshold = models.IntegerField(default=0)
    students_below_threshold = models.IntegerField(default=0)
    
    # Finance
    fees_collected_today = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('school', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.school.name} - {self.date}"
