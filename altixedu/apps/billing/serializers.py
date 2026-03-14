from rest_framework import serializers
from .models import (
    Subscription, SubscriptionTier, PaymentTransaction, Invoice,
    FreeSchoolPlan, GovtSchoolTier, UpgradePromotion, FeatureAccess
)


class SubscriptionTierSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionTier
        fields = [
            'id', 'name', 'display_name', 'monthly_price', 'annual_price',
            'max_students', 'max_teachers', 'features', 'support_level', 'trial_days'
        ]
    
    def get_features(self, obj):
        """Get all enabled features for this tier"""
        features = FeatureAccess.objects.filter(
            tier=obj,
            is_enabled=True
        ).values_list('feature', flat=True)
        return list(features)


class PaymentTransactionSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='subscription.school.name', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'school_name', 'amount', 'currency', 'payment_method',
            'status', 'transaction_id', 'created_at', 'completed_at', 'notes'
        ]
        read_only_fields = ['created_at', 'completed_at']


class InvoiceSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='subscription.school.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'school_name', 'amount', 'issued_at',
            'due_at', 'paid_at', 'status', 'is_overdue'
        ]
        read_only_fields = ['issued_at', 'paid_at']
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


class SubscriptionSerializer(serializers.ModelSerializer):
    tier_name = serializers.CharField(source='tier.display_name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    days_until_renewal = serializers.SerializerMethodField()
    is_trial_active = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'school_name', 'tier_name', 'status', 'monthly_price',
            'payment_frequency', 'started_at', 'renewal_date', 'days_until_renewal',
            'trial_started_at', 'trial_ends_at', 'is_trial_active',
            'features', 'discount_percentage', 'special_notes'
        ]
        read_only_fields = ['started_at', 'renewal_date', 'trial_started_at', 'trial_ends_at']
    
    def get_days_until_renewal(self, obj):
        return obj.days_until_renewal()
    
    def get_is_trial_active(self, obj):
        return obj.is_trial_active()
    
    def get_features(self, obj):
        """Get all features available in current tier"""
        if not obj.tier:
            return []
        features = FeatureAccess.objects.filter(
            tier=obj.tier,
            is_enabled=True
        ).values_list('feature', flat=True)
        return list(features)


class FreeSchoolPlanSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = FreeSchoolPlan
        fields = [
            'id', 'school_name', 'students_count', 'teachers_count',
            'daily_active_users', 'features_used', 'engagement_score',
            'is_ready_to_upgrade', 'upgrade_trigger', 'created_at'
        ]
        read_only_fields = [
            'created_at', 'engagement_score', 'is_ready_to_upgrade', 'upgrade_trigger'
        ]


class GovtSchoolTierSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    effective_price = serializers.SerializerMethodField()
    
    class Meta:
        model = GovtSchoolTier
        fields = [
            'id', 'school_name', 'registration_number', 'approved_at',
            'billing_cycle', 'monthly_cost', 'effective_price',
            'unlimited_students', 'unlimited_teachers', 'priority_support',
            'is_bulk_purchase', 'bulk_school_count', 'bulk_discount_percentage',
            'tender_reference', 'is_approved', 'next_payment_date'
        ]
        read_only_fields = ['approved_at', 'effective_price']
    
    def get_effective_price(self, obj):
        return float(obj.get_effective_price())


class UpgradePromotionSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = UpgradePromotion
        fields = [
            'id', 'code', 'display_name', 'promo_type', 'discount_percentage',
            'applicable_tiers', 'starts_at', 'expires_at', 'is_valid',
            'current_uses', 'max_uses', 'usage_percentage'
        ]
        read_only_fields = ['starts_at', 'expires_at', 'current_uses']
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def get_usage_percentage(self, obj):
        if obj.max_uses is None:
            return None
        return (obj.current_uses / obj.max_uses * 100) if obj.max_uses > 0 else 0
