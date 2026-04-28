from rest_framework import serializers
from apps.teachers.models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id',
            'school',
            'school_name',
            'user',
            'user_email',
            'employment_date',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
