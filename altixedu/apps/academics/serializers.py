from rest_framework import serializers
from .models import Classroom, Subject, TeacherSubject, Exam, ExamResult


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name', 'grade_level', 'school']
        read_only_fields = ['school']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'school']
        read_only_fields = ['school']


class TeacherSubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(
        source='teacher.get_full_name',
        read_only=True
    )
    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )
    classroom_name = serializers.CharField(
        source='classroom.name',
        read_only=True
    )

    class Meta:
        model = TeacherSubject
        fields = [
            'id',
            'teacher',
            'teacher_name',
            'subject',
            'subject_name',
            'classroom',
            'classroom_name'
        ]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name', 'school', 'start_date', 'end_date']
        read_only_fields = ['school']


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )

    class Meta:
        model = ExamResult
        fields = [
            'id',
            'exam',
            'student',
            'student_name',
            'subject',
            'subject_name',
            'score',
            'created_by',
            'created_by_name',
            'created_at'
        ]