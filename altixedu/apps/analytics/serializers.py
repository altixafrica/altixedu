from rest_framework import serializers
from .models import AnalyticsDashboard, SchoolPerformanceMetric


class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsDashboard
        fields = '__all__'


class SchoolPerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolPerformanceMetric
        fields = '__all__'
