from django.db import models
from apps.schools.models import School
from apps.accounts.models import User


class Bursar(models.Model):
    """
    Bursar profile linked to User account.
    Manages school finances and fees.
    """
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='bursars'
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bursar_profile',
        limit_choices_to={'role': 'bursar'},
        help_text="Optional linked user account for login"
    )
    
    managed_fees = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="Fee structure and payment details"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} ({self.school.name})"
        return f"Bursar ID: {self.id} ({self.school.name})"
    
    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        return f"Bursar {self.id}"
