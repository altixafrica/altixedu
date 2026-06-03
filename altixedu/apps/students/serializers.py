from rest_framework import serializers
from .models import Student
from apps.accounts.models import User
from apps.accounts.role_models import ParentStudentLink


class ParentLinkSerializer(serializers.ModelSerializer):
    """Serializer for parent-student relationships using ParentStudentLink model."""
    parent_name = serializers.CharField(
        source='parent.get_full_name',
        read_only=True
    )
    parent_email = serializers.CharField(
        source='parent.email',
        read_only=True
    )

    class Meta:
        model = ParentStudentLink
        fields = [
            'id', 'parent', 'parent_name', 'parent_email',
            'relationship', 'is_primary', 'receives_progress_reports',
            'can_authorize_absence', 'can_view_grades'
        ]
        read_only_fields = ['parent_name', 'parent_email']


class StudentSerializer(serializers.ModelSerializer):
    parent_links = ParentLinkSerializer(
        many=True,
        read_only=True
    )
    classroom_name = serializers.CharField(
        source='classroom.name',
        read_only=True
    )

    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'last_name',
            'admission_number',
            'date_of_birth',
            'gender',
            'status',
            'classroom',
            'classroom_name',
            'parent_links',
            'photo',
            'enrollment_date',
            'school'
        ]
        read_only_fields = ['school']