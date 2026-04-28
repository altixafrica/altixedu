"""
Health and Medical Records Models for Students
"""

from django.db import models
from apps.students.models import Student
from apps.schools.models import School
from encryption import EncryptedField, EncryptedCharField


class StudentHealthRecord(models.Model):
    """Medical and health information for students"""
    
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='health_record'
    )
    
    # Medical conditions
    medical_conditions = models.TextField(
        blank=True,
        help_text="Comma-separated list of medical conditions (e.g., Asthma, Diabetes)"
    )
    
    # Allergies - encrypted for privacy
    allergies = EncryptedField(
        blank=True,
        help_text="Allergies and sensitivities (food, medications, environmental)"
    )
    
    # Current medications - encrypted
    medications = EncryptedField(
        blank=True,
        help_text="Current medications and dosages"
    )
    
    # Insurance information - encrypted
    insurance_provider = EncryptedCharField(
        max_length=255,
        blank=True,
        help_text="Health insurance provider name"
    )
    
    insurance_policy_number = EncryptedCharField(
        max_length=100,
        blank=True,
        help_text="Insurance policy/member ID"
    )
    
    # Immunization status
    immunization_status = models.CharField(
        max_length=50,
        choices=[
            ('up_to_date', 'Up to Date'),
            ('needs_update', 'Needs Update'),
            ('unknown', 'Unknown'),
        ],
        blank=True
    )
    
    # Blood type
    blood_type = models.CharField(
        max_length=5,
        choices=[
            ('O+', 'O+'), ('O-', 'O-'),
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
        ],
        blank=True,
        help_text="Student blood type"
    )
    
    # Physical fitness information
    height_cm = models.FloatField(
        null=True,
        blank=True,
        help_text="Height in centimeters"
    )
    
    weight_kg = models.FloatField(
        null=True,
        blank=True,
        help_text="Weight in kilograms"
    )
    
    # Vision and hearing
    wears_glasses = models.BooleanField(default=False)
    hearing_impairment = models.BooleanField(default=False)
    
    # Special needs
    special_needs = models.TextField(
        blank=True,
        help_text="Any special needs or accommodations required"
    )
    
    # Last checkup date
    last_medical_checkup = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last medical checkup"
    )
    
    # Additional notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Health Record - {self.student.first_name} {self.student.last_name}"


class StudentEmergencyContact(models.Model):
    """Multiple emergency contacts for each student"""
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    
    # Contact information - encrypted
    name = EncryptedCharField(max_length=200)
    relationship = models.CharField(
        max_length=50,
        help_text="Relationship to student (Parent, Guardian, Relative, etc.)"
    )
    phone_number = EncryptedCharField(max_length=20)
    email = EncryptedCharField(max_length=255, blank=True)
    address = EncryptedField(blank=True)
    
    # Priority - first contact called in emergency
    is_primary = models.BooleanField(default=False)
    priority_order = models.IntegerField(default=0)
    
    # Contact preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('phone', 'Phone'),
            ('email', 'Email'),
            ('sms', 'SMS'),
        ],
        default='phone'
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority_order', '-is_primary']
    
    def __str__(self):
        return f"{self.name} ({self.relationship})"


class HealthMetric(models.Model):
    """Track health metrics over time (for health monitoring)"""
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('height', 'Height'),
            ('weight', 'Weight'),
            ('blood_pressure', 'Blood Pressure'),
            ('bmi', 'BMI'),
            ('fitness_score', 'Fitness Score'),
        ]
    )
    
    value = models.CharField(max_length=100)
    unit = models.CharField(
        max_length=20,
        help_text="Unit of measurement (cm, kg, mmHg, etc.)"
    )
    
    recorded_date = models.DateField()
    recorded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['teacher', 'admin']},
        help_text="Staff member who recorded the metric"
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_date']
    
    def __str__(self):
        return f"{self.student} - {self.metric_type}: {self.value}{self.unit}"
