from django.db import models
from apps.schools.models import School
from apps.accounts.models import User


class Student(models.Model):

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('inactive', 'Inactive'),
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='students'
    )

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profile',
        help_text="Optional linked user account for login"
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    admission_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique per school"
    )

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    enrollment_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    photo_url = models.URLField(
        null=True,
        blank=True,
        help_text="Student photo URL"
    )

    classroom = models.ForeignKey(
        'academics.Classroom',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='students'
    )

    parents = models.ManyToManyField(
        User,
        through='StudentParent',
        related_name='children'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class StudentParent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        User,
        limit_choices_to={'role': 'parent'},
        on_delete=models.CASCADE
    )
    relationship = models.CharField(
        max_length=50,
        help_text="e.g., Mother, Father, Guardian"
    )

    class Meta:
        unique_together = ('student', 'parent')

    def __str__(self):
        return f"{self.parent.get_full_name()} -> {self.student.first_name}"


class Parent(models.Model):
    """
    Parent profile linked to User account.
    A parent can have multiple children (M2M to Student).
    """
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='parents'
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parent_profile',
        limit_choices_to={'role': 'parent'},
        help_text="Optional linked user account for login"
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Parent contact phone number"
    )
    
    address = models.TextField(
        null=True,
        blank=True,
        help_text="Residential address"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'user__last_name']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} ({self.school.name})"
        return f"Parent ID: {self.id} ({self.school.name})"
    
    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        return f"Parent {self.id}"
    
    @property
    def children(self):
        """Get all children (students) of this parent"""
        return Student.objects.filter(
            studentparent__parent=self.user
        ).distinct() if self.user else Student.objects.none()
