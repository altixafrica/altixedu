from django.db import models
from django.utils import timezone
from apps.schools.models import School


class AcademicYear(models.Model):
    """
    Represents an academic year for a school.
    Each school can have multiple academic years.
    Supports African academic year formats (Jan-Dec, Sep-Aug, etc.)
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='academic_years'
    )
    year = models.CharField(
        max_length=20,
        help_text="e.g., 2025/2026"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(
        default=False,
        help_text="Only one academic year can be active per school"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('school', 'year')
        ordering = ['-year']
        indexes = [
            models.Index(fields=['school', 'is_active']),
        ]

    def __str__(self):
        return f"{self.school.name} - {self.year}"
    
    @property
    def is_current(self):
        """Check if this year is the current active year"""
        return self.is_active


class Term(models.Model):
    """
    Represents a term (semester/quarter) within an academic year.
    African schools typically have 3 terms per year.
    Supports flexible term structures.
    """
    TERM_CHOICES = (
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
        ('term4', 'Term 4'),  # Some schools use 4 quarters
        ('semester1', 'Semester 1'),
        ('semester2', 'Semester 2'),
        ('quarter1', 'Quarter 1'),
        ('quarter2', 'Quarter 2'),
        ('quarter3', 'Quarter 3'),
        ('quarter4', 'Quarter 4'),
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='terms'
    )
    name = models.CharField(
        max_length=20,
        choices=TERM_CHOICES,
        help_text="Term identifier (Term 1, Semester 1, etc.)"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(
        default=False,
        help_text="Only one term can be active per academic year"
    )
    school_reopens = models.DateField(
        null=True,
        blank=True,
        help_text="Date when school reopens after break"
    )
    school_closes = models.DateField(
        null=True,
        blank=True,
        help_text="Date when school closes for break"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('academic_year', 'name')
        ordering = ['academic_year', 'start_date']
        indexes = [
            models.Index(fields=['academic_year', 'is_active']),
        ]

    def __str__(self):
        return f"{self.academic_year.year} - {self.get_name_display()}"
    
    @property
    def duration_days(self):
        """Return number of days in this term"""
        return (self.end_date - self.start_date).days


class Subject(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

    class Meta:
        unique_together = ('school', 'code')
        indexes = [
            models.Index(fields=['school', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Classroom(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='classrooms'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classrooms'
    )
    name = models.CharField(max_length=50)
    grade_level = models.CharField(max_length=20)
    class_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_taught'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('school', 'name', 'academic_year')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.grade_level}"


class TeacherSubject(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Reference for multi-tenant data isolation"
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='subjects_taught'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject', 'classroom')
        ordering = ['teacher', 'subject']

    def __str__(self):
        teacher_name = self.teacher.user.get_full_name() if self.teacher.user else self.teacher.id
        return f"{teacher_name} - {self.subject.name}"


class Exam(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class ExamResult(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.FloatField()
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'teacher'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'student', 'subject')

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.score}"
