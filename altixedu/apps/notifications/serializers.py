from rest_framework import serializers
from .models import Message, StudentAIInsights, SchoolSetting, RoleSetting


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    receiver_role = serializers.CharField(source='receiver.role', read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'sender_role',
            'receiver', 'receiver_name', 'receiver_role',
            'content', 'read', 'sent_at', 'student', 'student_name'
        ]
        read_only_fields = ['sent_at', 'sender']

    def get_student_name(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name}"
        return None


class StudentAIInsightsSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    admission_number = serializers.CharField(
        source='student.admission_number',
        read_only=True
    )
    risk_level = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    classroom = serializers.CharField(
        source='student.classroom.name',
        read_only=True
    )

    class Meta:
        model = StudentAIInsights
        fields = [
            'id', 'student', 'student_name', 'admission_number', 'classroom',
            'attendance_risk', 'performance_risk', 'overall_risk', 'risk_level',
            'attendance_percentage', 'average_grade', 'days_absent',
            'low_attendance', 'low_performance', 'flagged_subjects',
            'recommendations',
            'calculated_at', 'created_at'
        ]
        read_only_fields = ['calculated_at', 'created_at']
    
    def get_risk_level(self, obj):
        """Get human-readable risk level."""
        return obj.get_risk_level()
    
    def get_recommendations(self, obj):
        """Get actionable recommendations."""
        return obj.get_recommendations()


class SchoolSettingSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = SchoolSetting
        fields = [
            'school', 'school_name', 'logo_url',
            'primary_color', 'secondary_color',
            'school_year', 'attendance_threshold', 'performance_threshold',
            'enable_parent_portal', 'enable_student_portal', 'enable_teacher_portal',
            'notification_email', 'enable_email_alerts', 'enable_sms_alerts',
            'default_fee_structure', 'created_at', 'updated_at'
        ]


class RoleSettingSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = RoleSetting
        fields = [
            'id', 'role', 'school', 'school_name',
            'key', 'value', 'created_at', 'updated_at'
        ]
