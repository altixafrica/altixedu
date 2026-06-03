"""
Core models for world-class compliance, auditing, and system infrastructure.
Includes AuditLog, OfflineSync, CurrencyExchange rate tracking.
"""
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.accounts.models import User
from apps.schools.models import School
import json


class AuditLog(models.Model):
    """
    Comprehensive audit trail for world-class compliance.
    Tracks all CREATE, UPDATE, DELETE operations with user, timestamp, and change details.
    
    Usage:
        AuditLog.log_change(user, instance, action='update', changes={'field': (old, new)})
    """
    ACTION_CHOICES = (
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('soft_delete', 'Soft Deleted'),
        ('restore', 'Restored'),
        ('export', 'Exported'),
        ('import', 'Imported'),
        ('payment', 'Payment Recorded'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('other', 'Other'),
    )
    
    # What changed
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        help_text="Django content type of the affected model"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID of the object that was changed"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Who changed it
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    
    # What action
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    
    # Details of the change
    description = models.TextField(
        help_text="Human-readable description of the change"
    )
    changes = models.JSONField(
        default=dict,
        help_text="Dictionary of {field: [old_value, new_value]} for updates"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user who made the change"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string from browser/client"
    )
    
    # Timestamp
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the change was made"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['school', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name_plural = "Audit Logs"
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.content_type.name} #{self.object_id} by {self.user} at {self.timestamp}"
    
    @classmethod
    def log_change(cls, user, instance, action='update', changes=None, school=None, ip_address=None, user_agent=None):
        """
        Log a change to the database.
        
        Args:
            user: User who made the change
            instance: Model instance that was changed
            action: Type of action (create, update, delete, etc.)
            changes: Dict of {field: [old_value, new_value]}
            school: School instance (if not on user, use this)
            ip_address: IP address of requester
            user_agent: User agent string
        
        Returns:
            AuditLog instance created
        """
        if school is None:
            school = getattr(user, 'school', None)
            if school is None:
                school = getattr(instance, 'school', None)
        
        if school is None:
            # Skip logging if no school context
            return None
        
        description = f"{action.title()} {instance.__class__.__name__} #{instance.id}"
        
        return cls.objects.create(
            content_type=ContentType.objects.get_for_model(instance.__class__),
            object_id=instance.id,
            user=user,
            school=school,
            action=action,
            description=description,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @classmethod
    def get_object_history(cls, instance):
        """Get all audit logs for a specific object"""
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return cls.objects.filter(
            content_type=content_type,
            object_id=instance.id
        ).order_by('-timestamp')


class OfflineAttendanceSync(models.Model):
    """
    Model for syncing offline attendance records.
    Used when teachers mark attendance without internet connection.
    
    Workflow:
        1. Teacher marks attendance offline (stored in browser localStorage)
        2. Frontend batches records in OfflineAttendanceSync
        3. When online, POST /api/offline-sync/attendance/ to sync
        4. Server applies all records atomically
        5. Frontend clears localStorage cache
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='offline_attendance_syncs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offline_attendance_syncs',
        help_text="Teacher who marked attendance offline"
    )
    
    # Sync details
    sync_uuid = models.CharField(
        max_length=36,
        unique=True,
        help_text="UUID for idempotency (prevent duplicate syncs)"
    )
    records = models.JSONField(
        help_text="Array of {date, classroom_id, attendance_data} records"
    )
    num_records = models.IntegerField(
        help_text="Number of attendance records in this sync"
    )
    
    # Status
    SYNC_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Failed'),
    )
    status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default='pending'
    )
    
    # Results
    synced_count = models.IntegerField(
        default=0,
        help_text="Number of records successfully synced"
    )
    error_count = models.IntegerField(
        default=0,
        help_text="Number of records that failed"
    )
    error_details = models.JSONField(
        default=list,
        help_text="Array of {record_index, error_message} for failed records"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this sync was processed"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', '-created_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['sync_uuid']),
        ]
    
    def __str__(self):
        return f"Sync {self.sync_uuid[:8]}... ({self.num_records} records) - {self.status}"
    
    def mark_completed(self, synced_count, error_count=0, error_details=None):
        """Mark sync as completed"""
        self.status = 'partial' if error_count > 0 else 'completed'
        self.synced_count = synced_count
        self.error_count = error_count
        self.error_details = error_details or []
        self.synced_at = timezone.now()
        self.save()


class CurrencyExchange(models.Model):
    """
    Currency exchange rates for multi-currency support.
    Base currency: USD
    Updates daily from external source or manual entry.
    
    Usage:
        rate = CurrencyExchange.get_rate('KES')  # Get KES/USD rate
        amount_usd = amount_local / rate
    """
    currency_code = models.CharField(
        max_length=3,
        unique_for_date='date',
        help_text="ISO 4217 currency code (KES, UGX, NGN, etc.)"
    )
    currency_name = models.CharField(
        max_length=100,
        help_text="Currency name (e.g., Kenyan Shilling)"
    )
    
    # Exchange rate to USD
    rate = models.FloatField(
        help_text="Exchange rate: 1 USD = ? (currency_code)"
    )
    inverse_rate = models.FloatField(
        help_text="Inverse rate: 1 (currency_code) = ? USD"
    )
    
    # Metadata
    date = models.DateField(
        default=timezone.now,
        help_text="Date this rate was recorded"
    )
    source = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Entry'),
            ('api', 'API (exchangerate-api.com)'),
            ('fixer', 'Fixer.io API'),
            ('other', 'Other Source'),
        ],
        default='api'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Use this rate in conversions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', 'currency_code']
        indexes = [
            models.Index(fields=['currency_code', '-date']),
            models.Index(fields=['is_active', '-date']),
        ]
        unique_together = ('currency_code', 'date')
    
    def __str__(self):
        return f"{self.currency_code} - 1 USD = {self.rate} ({self.date})"
    
    @classmethod
    def get_rate(cls, currency_code, date=None):
        """Get most recent exchange rate for a currency"""
        if date is None:
            date = timezone.now().date()
        
        rate = cls.objects.filter(
            currency_code=currency_code,
            date__lte=date,
            is_active=True
        ).order_by('-date').first()
        
        if rate:
            return rate.rate
        return 1.0  # Default to 1:1 if not found
    
    @classmethod
    def convert_to_usd(cls, amount, from_currency):
        """Convert amount from local currency to USD"""
        if from_currency == 'USD':
            return amount
        
        rate = cls.get_rate(from_currency)
        return amount / rate if rate > 0 else 0.0
    
    @classmethod
    def convert_from_usd(cls, amount, to_currency):
        """Convert amount from USD to local currency"""
        if to_currency == 'USD':
            return amount
        
        rate = cls.get_rate(to_currency)
        return amount * rate


class SystemSetting(models.Model):
    """
    Global system settings for Altixedu platform.
    Used for configuration flags, feature toggles, maintenance settings.
    """
    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Configuration key (e.g., 'MAINTENANCE_MODE')"
    )
    value = models.TextField(
        help_text="Configuration value (JSON for complex types)"
    )
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
            ('list', 'List'),
        ],
        default='string'
    )
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of this setting"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['key']
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"{self.key} = {self.value}"
    
    @classmethod
    def get(cls, key, default=None):
        """Get setting by key"""
        try:
            setting = cls.objects.get(key=key)
            if setting.value_type == 'boolean':
                return setting.value.lower() == 'true'
            elif setting.value_type == 'integer':
                return int(setting.value)
            elif setting.value_type == 'json':
                return json.loads(setting.value)
            elif setting.value_type == 'list':
                return json.loads(setting.value)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set(cls, key, value, value_type='string', description=''):
        """Set or create setting"""
        setting, created = cls.objects.get_or_create(key=key)
        setting.value = str(value) if value_type != 'json' else json.dumps(value)
        setting.value_type = value_type
        if description:
            setting.description = description
        setting.save()
        return setting
