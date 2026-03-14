from rest_framework import serializers
from .models import Student, StudentParent
from apps.accounts.models import User


class StudentParentSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source='parent.get_full_name',
        read_only=True
    )

    class Meta:
        model = StudentParent
        fields = ['id', 'parent', 'parent_name', 'relationship']


class StudentSerializer(serializers.ModelSerializer):
    parents = StudentParentSerializer(
        source='studentparent_set',
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
            'parents',
            'photo',
            'enrollment_date',
            'school'
        ]
        read_only_fields = ['school']