from django.db import models
import datetime
from apps.students.models import Student
from apps.schools.models import School
from apps.accounts.models import User


class Fee(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class StudentFee(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fees'
    )
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    amount_paid = models.FloatField(default=0)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'bursar'}
    )
    history = models.JSONField(
        default=list,
        help_text="Payment history with amounts, timestamps, and who recorded"
    )

    class Meta:
        unique_together = ('student', 'fee')

    def __str__(self):
        return f"{self.student} - {self.fee.name} - Paid: {self.paid}"

    def add_payment(self, amount, user):
        """
        Add a payment to this student fee with history tracking.
        Automatically updates amount_paid, paid status, and records the edit.
        """
        self.amount_paid += amount
        self.paid = self.amount_paid >= self.fee.amount
        
        # Append edit to history
        self.history.append({
            "amount_added": amount,
            "by": user.username,
            "by_full_name": user.get_full_name(),
            "date": str(datetime.datetime.now()),
            "total_paid_after": self.amount_paid
        })
        
        self.recorded_by = user
        self.save()
