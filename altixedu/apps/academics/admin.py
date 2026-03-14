from django.contrib import admin
from .models import (
    Subject,
    Classroom,
    TeacherSubject,
    Exam,
    ExamResult,
    AcademicYear
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'school')
    list_filter = ('school',)
    search_fields = ('name', 'code')


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'school', 'start_date', 'end_date', 'is_active')
    list_filter = ('school', 'is_active', 'start_date')
    search_fields = ('year',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Academic Year', {'fields': ('school', 'year')}),
        ('Duration', {'fields': ('start_date', 'end_date')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade_level', 'school', 'academic_year', 'class_teacher')
    list_filter = ('school', 'grade_level', 'academic_year')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'classroom', 'school')
    list_filter = ('school', 'classroom', 'subject')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'subject__name')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'start_date', 'end_date')
    list_filter = ('school', 'start_date')
    search_fields = ('name',)


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'subject', 'score')
    list_filter = ('exam', 'subject')
    search_fields = ('student__first_name', 'student__last_name')
