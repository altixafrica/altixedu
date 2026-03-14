from django.contrib import admin
from .models import (
    SubscriptionTier, Subscription, PaymentTransaction, Invoice,
    FreeSchoolPlan, GovtSchoolTier, FeatureAccess, UpgradePromotion,
    BillingAlert
)


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'max_students', 'max_teachers', 'support_level']
    list_filter = ['name', 'support_level']
    search_fields = ['name', 'display_name']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'school', 'tier', 'status', 'started_at', 'renewal_date']
    list_filter = ['status', 'tier', 'started_at']
    search_fields = ['school__name']
    readonly_fields = ['started_at']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscription', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subscription__school__name', 'stripe_transaction_id']
    readonly_fields = ['created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'subscription', 'amount', 'status', 'issued_at']
    list_filter = ['status', 'issued_at']
    search_fields = ['invoice_number', 'subscription__school__name']


@admin.register(FreeSchoolPlan)
class FreeSchoolPlanAdmin(admin.ModelAdmin):
    list_display = ['school', 'daily_active_users', 'engagement_score', 'created_at']
    search_fields = ['school__name']


@admin.register(GovtSchoolTier)
class GovtSchoolTierAdmin(admin.ModelAdmin):
    list_display = ['school', 'bulk_discount_percentage', 'is_approved', 'created_at']
    search_fields = ['school__name']


@admin.register(FeatureAccess)
class FeatureAccessAdmin(admin.ModelAdmin):
    list_display = ['tier', 'feature', 'is_enabled']
    list_filter = ['tier', 'is_enabled', 'feature']


@admin.register(UpgradePromotion)
class UpgradePromotionAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'starts_at', 'expires_at', 'is_active']
    list_filter = ['is_active', 'starts_at']


@admin.register(BillingAlert)
class BillingAlertAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'alert_type', 'created_at']
    list_filter = ['alert_type', 'created_at']
