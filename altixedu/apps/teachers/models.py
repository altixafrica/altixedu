from django.db import models
from apps.schools.models import School
from apps.accounts.models import User


class Teacher(models.Model):
    """
    Teacher profile linked to User account.
    A teacher can teach multiple subjects and classrooms.
    """
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('retired', 'Retired'),
        ('on_leave', 'On Leave'),
    )
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='teachers'
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_profile',
        limit_choices_to={'role': 'teacher'},
        help_text="Optional linked user account for login"
    )
    
    employment_date = models.DateField(
        help_text="Date teacher was employed"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # M2M relationships will be defined via TeacherSubject model
    # Teacher can teach multiple subjects and classrooms
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'user__last_name']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} ({self.school.name})"
        return f"Teacher ID: {self.id} ({self.school.name})"
    
    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        return f"Teacher {self.id}"
    
    @property
    def subjects(self):
        """Get all subjects taught by this teacher"""
        from apps.academics.models import TeacherSubject
        return TeacherSubject.objects.filter(teacher=self).values_list('subject', flat=True).distinct()
    
    @property
    def classrooms(self):
        """Get all classrooms this teacher teaches"""
        from apps.academics.models import TeacherSubject
        return TeacherSubject.objects.filter(teacher=self).values_list('classroom', flat=True).distinct()
