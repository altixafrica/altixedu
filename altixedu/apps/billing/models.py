from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.schools.models import School
import uuid


class SubscriptionTier(models.Model):
    """Define all subscription tiers and their features"""
    TIER_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('growth', 'Growth'),
        ('scale', 'Scale'),
        ('govt', 'Government'),
    ]
    
    name = models.CharField(max_length=50, unique=True, choices=TIER_CHOICES)
    display_name = models.CharField(max_length=100)  # "Starter Plan"
    
    # Pricing (in Naira)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Limits
    max_students = models.IntegerField()  # 200, 500, 2000, 5000, unlimited (999999)
    max_teachers = models.IntegerField()
    max_classrooms = models.IntegerField(default=100)
    
    # Features (JSON for flexibility)
    features = models.JSONField(default=dict)  # {'attendance': True, 'messaging': True, ...}
    
    # Support level
    SUPPORT_LEVELS = [
        ('email', 'Email Only'),
        ('chat', 'Chat + Email'),
        ('phone', 'Priority Phone Support'),
        ('vip', 'VIP/Dedicated'),
    ]
    support_level = models.CharField(max_length=20, choices=SUPPORT_LEVELS)
    
    # Trial days
    trial_days = models.IntegerField(default=30)  # Free tier: lifetime, others: 30 days
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Subscription Tiers"
        ordering = ['monthly_price']
    
    def __str__(self):
        return f"{self.display_name} (₦{self.monthly_price:,.0f}/month)"


class Subscription(models.Model):
    """Active subscription for a school"""
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='subscription')
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.SET_NULL, null=True)
    
    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_frequency = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annually'),
    ], default='monthly')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    
    # Trial info
    trial_started_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    is_trial_converted = models.BooleanField(default=False)
    
    # Billing dates
    started_at = models.DateTimeField(auto_now_add=True)
    renewal_date = models.DateTimeField()  # Next billing date
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe info
    stripe_customer_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Special pricing
    discount_percentage = models.IntegerField(default=0)  # For govt/bulk
    special_notes = models.TextField(blank=True)  # "Government tender - 100 schools"
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.tier.display_name} ({self.status})"
    
    def is_active(self):
        return self.status == 'active' and (self.cancelled_at is None or timezone.now() < self.cancelled_at)
    
    def is_trial_active(self):
        if not self.trial_ends_at:
            return False
        return timezone.now() < self.trial_ends_at
    
    def days_until_renewal(self):
        delta = self.renewal_date - timezone.now()
        return max(0, delta.days)
    
    def calculate_next_renewal_date(self):
        """Calculate next renewal date based on payment frequency"""
        if self.payment_frequency == 'monthly':
            return self.renewal_date + timedelta(days=30)
        elif self.payment_frequency == 'quarterly':
            return self.renewal_date + timedelta(days=90)
        elif self.payment_frequency == 'annual':
            return self.renewal_date + timedelta(days=365)
        return self.renewal_date


class PaymentTransaction(models.Model):
    """Track all payments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='transactions')
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')  # Nigerian Naira
    
    # Payment method
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card (Stripe)'),
        ('bank_transfer', 'Bank Transfer'),
        ('flutterwave', 'Flutterwave'),
        ('manual', 'Manual (Invoice)'),
    ]
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction IDs
    transaction_id = models.CharField(max_length=255, unique=True)  # Unique per transaction
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_invoice_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)  # For troubleshooting
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subscription.school.name} - ₦{self.amount:,.0f} ({self.status})"


class Invoice(models.Model):
    """Formal invoices for accounting"""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)  # INV-2024-001
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Dates
    issued_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # PDF storage
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    class Meta:
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.subscription.school.name}"
    
    def is_overdue(self):
        return self.status != 'paid' and timezone.now() > self.due_at


class FreeSchoolPlan(models.Model):
    """Tracks free tier usage for upsell"""
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='free_plan')
    
    # Created when school uses free tier
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Usage tracking
    students_count = models.IntegerField(default=0)
    teachers_count = models.IntegerField(default=0)
    daily_active_users = models.IntegerField(default=0)
    
    # Features used by free user
    features_used = models.JSONField(default=list)  # ['attendance', 'grades']
    
    # Engagement scoring
    last_activity_at = models.DateTimeField(null=True, blank=True)
    engagement_score = models.IntegerField(default=0)  # 0-100
    is_ready_to_upgrade = models.BooleanField(default=False)
    upgrade_trigger = models.CharField(
        max_length=100,
        blank=True,
        help_text="Why they should upgrade: 'storage_full', 'features_needed', etc"
    )
    
    # Upsell emails
    upgrade_email_sent_count = models.IntegerField(default=0)
    last_upgrade_email_sent = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Free School Plans"
    
    def __str__(self):
        return f"Free: {self.school.name} (Score: {self.engagement_score})"
    
    def should_trigger_upgrade(self):
        """Determine if user is ready to upgrade"""
        if self.students_count >= 200:
            self.upgrade_trigger = "storage_full"
            return True
        
        if len(self.features_used) >= 3:
            self.upgrade_trigger = "features_needed"
            return True
        
        # Active for 14+ days = might be ready
        days_active = (timezone.now() - self.created_at).days
        if days_active >= 14 and self.engagement_score > 50:
            self.upgrade_trigger = "power_user"
            return True
        
        return False


class GovtSchoolTier(models.Model):
    """Special tier for government schools"""
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='govt_tier')
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    
    # Proof of government affiliation
    registration_number = models.CharField(
        max_length=100,
        help_text="Ministry registration number"
    )
    ministry_approval_document = models.FileField(
        upload_to='govt_approvals/',
        null=True,
        blank=True,
        help_text="PDF of ministry approval letter"
    )
    approved_at = models.DateField()
    
    # Special government pricing
    BILLING_CYCLES = [
        ('monthly', 'Monthly (₦9,900)'),
        ('quarterly', 'Quarterly (₦29,700)'),
        ('annual', 'Annual (₦99,000)'),
    ]
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='quarterly')
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, default=9900)
    
    # Features
    unlimited_students = models.BooleanField(default=True)
    unlimited_teachers = models.BooleanField(default=True)
    unlimited_classrooms = models.BooleanField(default=True)
    priority_support = models.BooleanField(default=True)
    
    # Bulk purchase (for ministry tenders)
    is_bulk_purchase = models.BooleanField(default=False)
    bulk_school_count = models.IntegerField(default=1)  # Number of schools in this deal
    bulk_discount_percentage = models.IntegerField(default=0)  # 0=single, 30-40 for bulk
    tender_reference = models.CharField(max_length=255, blank=True)  # Ministry tender number
    
    # Status
    is_approved = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=255, blank=True)  # Admin email
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Next payment
    next_payment_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Government School Tiers"
    
    def __str__(self):
        if self.is_bulk_purchase:
            return f"Govt (Bulk): {self.school.name} ({self.bulk_school_count} schools)"
        return f"Govt: {self.school.name}"
    
    def get_effective_price(self):
        """Calculate price with bulk discount"""
        base_price = self.monthly_cost
        discount = base_price * (self.bulk_discount_percentage / 100)
        return base_price - discount


class FeatureAccess(models.Model):
    """Track which features are available to each tier"""
    FEATURE_CHOICES = [
        ('attendance', 'Attendance Tracking'),
        ('grades', 'Grade Management'),
        ('fees', 'Fee Tracking'),
        ('messaging', 'Parent Messaging'),
        ('ai_alerts', 'AI Risk Alerts'),
        ('bulk_import', 'Bulk Import'),
        ('sms_alerts', 'SMS Alerts'),
        ('advanced_reports', 'Advanced Reports'),
        ('pdf_export', 'PDF Export'),
        ('api_access', 'API Access'),
        ('student_portal', 'Student Portal'),
        ('custom_integration', 'Custom Integration'),
    ]
    
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE, related_name='feature_access')
    feature = models.CharField(max_length=50, choices=FEATURE_CHOICES)
    is_enabled = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('tier', 'feature')
        verbose_name_plural = "Feature Access"
    
    def __str__(self):
        return f"{self.tier.display_name} - {self.feature}"


class UpgradePromotion(models.Model):
    """Marketing promotions for upgrades"""
    PROMO_TYPES = [
        ('launch', 'Launch Offer'),
        ('seasonal', 'Seasonal'),
        ('referral', 'Referral'),
        ('govt', 'Government Bulk'),
    ]
    
    code = models.CharField(max_length=50, unique=True)  # "LAUNCH50", "GOVT40"
    display_name = models.CharField(max_length=200)  # "50% off Starter for first 3 months"
    
    promo_type = models.CharField(max_length=50, choices=PROMO_TYPES)
    description = models.TextField()
    
    # Discount
    discount_percentage = models.IntegerField()  # 50
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Eligibility
    applicable_tiers = models.JSONField(default=list)  # ['starter', 'growth']
    min_school_count = models.IntegerField(default=1)  # Minimum schools for bulk deals
    
    # Date range
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    
    # Usage tracking
    max_uses = models.IntegerField(null=True, blank=True)  # None = unlimited
    current_uses = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-starts_at']
    
    def __str__(self):
        return f"{self.code} - {self.discount_percentage}% off"
    
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.starts_at <= now <= self.expires_at and 
                (self.max_uses is None or self.current_uses < self.max_uses))
    
    def use_promo(self):
        """Increment use count"""
        if self.is_valid():
            self.current_uses += 1
            self.save()
            return True
        return False


class BillingAlert(models.Model):
    """Track billing issues (past due, etc)"""
    ALERT_TYPES = [
        ('trial_ending', 'Trial Ending Soon'),
        ('renewal_upcoming', 'Renewal Upcoming'),
        ('payment_failed', 'Payment Failed'),
        ('past_due', 'Payment Past Due'),
        ('upgrade_suggested', 'Upgrade Suggested'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='billing_alerts')
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    message = models.TextField()
    
    # Status
    is_resolved = models.BooleanField(default=False)
    
    # Communication
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subscription.school.name} - {self.alert_type}"
