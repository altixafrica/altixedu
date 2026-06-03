from django.db import models
from django.utils import timezone
import datetime
from decimal import Decimal
from apps.students.models import Student
from apps.schools.models import School
from apps.accounts.models import User


class Fee(models.Model):
    """Fee model with multi-currency support for African schools"""
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # Multi-currency support
    currency_code = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        help_text="Override school currency (e.g., KES, UGX, NGN). If null, uses school.currency_code"
    )
    description = models.TextField(null=True, blank=True)
    due_date_template = models.CharField(
        max_length=20,
        choices=[
            ('term1', 'Term 1'),
            ('term2', 'Term 2'),
            ('term3', 'Term 3'),
            ('monthly', 'Monthly'),
            ('custom', 'Custom Date'),
        ],
        default='term1',
        help_text="When this fee is typically due"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.school.name}"
    
    def get_currency(self):
        """Get currency code: use Fee currency if set, else School currency"""
        return self.currency_code or self.school.currency_code


class StudentFee(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fees'
    )
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
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
        payment_amount = Decimal(str(amount))
        self.amount_paid += payment_amount
        self.paid = self.amount_paid >= self.fee.amount
        
        # Append edit to history
        self.history.append({
            "amount_added": str(payment_amount),
            "by": user.username,
            "by_full_name": user.get_full_name(),
            "date": str(datetime.datetime.now()),
            "total_paid_after": str(self.amount_paid)
        })
        
        self.recorded_by = user
        self.save()


class PaymentReceipt(models.Model):
    """
    Payment receipt model for tracking and generating PDF receipts.
    Stores receipt details and PDF file path.
    SUPPORTS MULTI-CURRENCY for African schools.
    """
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('mobile_money', 'Mobile Money'),
        ('m_pesa', 'M-Pesa'),
        ('airtel_money', 'Airtel Money'),
        ('mtn_money', 'MTN Mobile Money'),
        ('flutterwave', 'Flutterwave'),
        ('other', 'Other'),
    )
    
    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name='receipts'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payment_receipts'
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='payment_receipts'
    )
    
    # Receipt details
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique receipt identifier"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount paid")
    # Multi-currency support
    currency_code = models.CharField(
        max_length=3,
        default="USD",
        help_text="Currency code (KES, UGX, NGN, GHS, ZAR, TZS, ETB, USD, etc.)"
    )
    amount_in_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Converted amount in USD for reporting (calculated via exchange rate)"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    description = models.TextField(null=True, blank=True)
    
    # Payment tracking
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payment_receipts_issued'
    )
    payment_date = models.DateTimeField(default=timezone.now)
    
    # File storage
    pdf_file = models.FileField(
        upload_to='payment_receipts/',
        null=True,
        blank=True,
        help_text="PDF receipt file"
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Soft-delete timestamp for audit trail"
    )
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['student', 'payment_date']),
            models.Index(fields=['school', 'payment_date']),
        ]
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.student} - {self.amount} {self.currency_code}"
    
    @staticmethod
    def generate_receipt_number(school_id):
        """Generate unique receipt number: RCP-{SCHOOL_ID}-{DATE}-{SEQUENCE}"""
        today = timezone.now().date()
        count = PaymentReceipt.objects.filter(
            school_id=school_id,
            payment_date__date=today,
            deleted_at__isnull=True
        ).count() + 1
        return f"RCP-{school_id}-{today.strftime('%Y%m%d')}-{count:04d}"
