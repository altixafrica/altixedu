"""
URL Configuration for Billing App
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BillingPortfolioView,
    FlutterwaveCheckoutView,
    FlutterwaveVerifyView,
    FlutterwaveWebhookView,
    PricingPageView,
    SubscriptionViewSet,
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
    path('portfolio/', BillingPortfolioView.as_view(), name='billing-portfolio'),
    
    # Flutterwave checkout endpoints
    path('checkout/initialize/', FlutterwaveCheckoutView.as_view(), name='checkout-initialize'),
    path('checkout/verify/', FlutterwaveVerifyView.as_view(), name='checkout-verify'),
    path('flutterwave/webhook/', FlutterwaveWebhookView.as_view(), name='flutterwave-webhook'),
    
    # Subscription management
    path('upgrade/', UpgradeDowngradeView.as_view(), name='upgrade-downgrade'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    
    # Payment and invoice history
    path('payment-history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('invoices/', InvoiceView.as_view(), name='invoices'),
]
