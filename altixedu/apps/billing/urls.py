"""
URL Configuration for Billing App
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PricingPageView,
    SubscriptionViewSet,
    StripeSubscriptionView,
    StripeWebhookView,
    UpgradeDowngradeView,
    CancelSubscriptionView,
    PaymentHistoryView,
    InvoiceView
)

# Create router for ModelViewSet
router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

app_name = 'billing'

urlpatterns = [
    # Router endpoints for subscriptions
    path('', include(router.urls)),
    
    # Public endpoints
    path('pricing/', PricingPageView.as_view(), name='pricing-page'),
    
    # Stripe payment endpoints
    path('stripe-payment/', StripeSubscriptionView.as_view(), name='stripe-payment'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # Subscription management
    path('upgrade/', UpgradeDowngradeView.as_view(), name='upgrade-downgrade'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    
    # Payment and invoice history
    path('payment-history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('invoices/', InvoiceView.as_view(), name='invoices'),
]
