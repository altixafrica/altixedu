from rest_framework import serializers
from .models import Classroom, Subject, TeacherSubject, Exam, ExamResult, AcademicYear, Term


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
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
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
    student_name = serializers.SerializerMethodField()
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
        read_only_fields = ['created_by', 'created_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip()


class TermSerializer(serializers.ModelSerializer):
    """Serializer for Term model - semester/quarter within academic year"""
    academic_year_display = serializers.CharField(source='academic_year.year', read_only=True)
    term_name = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Term
        fields = [
            'id',
            'academic_year',
            'academic_year_display',
            'name',
            'term_name',
            'start_date',
            'end_date',
            'school_reopens',
            'school_closes',
            'is_active',
            'duration_days',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'duration_days']


class AcademicYearSerializer(serializers.ModelSerializer):
    """Serializer for AcademicYear with nested terms"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    terms = TermSerializer(many=True, read_only=True)
    
    class Meta:
        model = AcademicYear
        fields = [
            'id',
            'school',
            'school_name',
            'year',
            'start_date',
            'end_date',
            'is_active',
            'is_current',
            'terms',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_current']
