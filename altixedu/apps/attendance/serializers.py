from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    recorded_by_name = serializers.CharField(
        source='recorded_by.get_full_name',
        read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'student_name',
            'school',
            'date',
            'status',
            'recorded_by',
            'recorded_by_name'
        ]
        read_only_fields = ['school']