"""
Serializers for Health and Medical Records
"""

from rest_framework import serializers
from apps.students.health_models import (
    StudentHealthRecord,
    StudentEmergencyContact,
    HealthMetric
)


class StudentHealthRecordSerializer(serializers.ModelSerializer):
    """Serializer for student health records"""
    student_full_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = StudentHealthRecord
        fields = [
            'id', 'student', 'student_full_name', 'medical_conditions',
            'allergies', 'medications', 'insurance_provider',
            'insurance_policy_number', 'immunization_status', 'blood_type',
            'height_cm', 'weight_kg', 'wears_glasses', 'hearing_impairment',
            'special_needs', 'last_medical_checkup', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StudentEmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for student emergency contacts"""
    
    class Meta:
        model = StudentEmergencyContact
        fields = [
            'id', 'student', 'name', 'relationship', 'phone_number',
            'email', 'address', 'is_primary', 'priority_order',
            'preferred_contact_method', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class HealthMetricSerializer(serializers.ModelSerializer):
    """Serializer for health metrics tracking"""
    recorded_by_name = serializers.CharField(
        source='recorded_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = HealthMetric
        fields = [
            'id', 'student', 'metric_type', 'value', 'unit',
            'recorded_date', 'recorded_by', 'recorded_by_name', 'notes',
            'created_at'
        ]
        read_only_fields = ['created_at']
