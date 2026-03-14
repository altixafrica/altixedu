from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import stripe
import uuid
import logging

from apps.accounts.permissions import IsSchoolAdmin
from apps.schools.models import School
from .models import (
    Subscription, SubscriptionTier, PaymentTransaction, Invoice,
    FreeSchoolPlan, GovtSchoolTier, UpgradePromotion, BillingAlert,
    FeatureAccess
)
from .serializers import (
    SubscriptionSerializer, PaymentTransactionSerializer,
    InvoiceSerializer, SubscriptionTierSerializer
)

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PricingPageView(APIView):
    """Public endpoint for pricing page"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get all tiers and features"""
        tiers = SubscriptionTier.objects.all()
        
        tiers_data = []
        for tier in tiers:
            features = FeatureAccess.objects.filter(
                tier=tier,
                is_enabled=True
            ).values_list('feature', flat=True)
            
            tiers_data.append({
                'id': tier.id,
                'name': tier.name,
                'display_name': tier.display_name,
                'monthly_price': float(tier.monthly_price),
                'annual_price': float(tier.annual_price) if tier.annual_price else None,
                'max_students': tier.max_students,
                'max_teachers': tier.max_teachers,
                'features': list(features),
                'support_level': tier.support_level,
                'trial_days': tier.trial_days,
            })
        
        return Response({
            'tiers': tiers_data,
            'currency': 'NGN',
            'note': 'Government schools get ₦9,900/month special pricing'
        })


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Manage school subscriptions"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_queryset(self):
        """School can only see their own subscription"""
        user = self.request.user
        if user.role == 'superadmin':
            return Subscription.objects.all()
        return Subscription.objects.filter(school=user.school)
    
    def get_object(self):
        """Get school's subscription"""
        return Subscription.objects.get(school=self.request.user.school)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current school's subscription"""
        try:
            subscription = Subscription.objects.get(school=request.user.school)
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def check_upgrade_eligibility(self, request):
        """Check if school can upgrade"""
        try:
            subscription = Subscription.objects.get(school=request.user.school)
        except Subscription.DoesNotExist:
            return Response({'eligible': True, 'reason': 'No subscription yet'})
        
        # Can upgrade if active or trial
        if subscription.status in ['trial', 'active']:
            return Response({'eligible': True, 'current_tier': subscription.tier.name})
        
        return Response({'eligible': False, 'reason': 'Subscription not active'})


class StripeSubscriptionView(APIView):
    """Create Stripe subscription for payment"""
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def post(self, request):
        """
        Create a new Stripe subscription
        
        Body:
        {
            "tier_id": 1,
            "payment_frequency": "monthly",
            "promo_code": "LAUNCH50" (optional)
        }
        """
        school = request.user.school
        tier_id = request.data.get('tier_id')
        payment_frequency = request.data.get('payment_frequency', 'monthly')
        promo_code = request.data.get('promo_code')
        
        # Validate tier
        try:
            tier = SubscriptionTier.objects.get(id=tier_id)
        except SubscriptionTier.DoesNotExist:
            return Response(
                {'error': 'Tier not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check promo code
        discount_percentage = 0
        if promo_code:
            try:
                promo = UpgradePromotion.objects.get(code=promo_code)
                if promo.is_valid() and tier.name in promo.applicable_tiers:
                    discount_percentage = promo.discount_percentage
                    promo.use_promo()
            except UpgradePromotion.DoesNotExist:
                return Response(
                    {'error': f'Promo code "{promo_code}" not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate price
        if payment_frequency == 'monthly':
            amount = tier.monthly_price
        elif payment_frequency == 'quarterly':
            amount = tier.monthly_price * 3 * 0.95  # 5% discount for quarterly
        elif payment_frequency == 'annual':
            amount = tier.annual_price or tier.monthly_price * 12 * 0.85  # 15% discount
        else:
            return Response(
                {'error': 'Invalid payment frequency'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply promo discount
        if discount_percentage > 0:
            amount = amount * (1 - discount_percentage / 100)
        
        try:
            # Create or get Stripe customer
            if not school.subscription.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=school.name,
                    description=f"School: {school.name}",
                    metadata={
                        'school_id': school.id,
                        'school_name': school.name,
                    }
                )
                school.subscription.stripe_customer_id = customer.id
                school.subscription.save()
            else:
                customer = stripe.Customer.retrieve(school.subscription.stripe_customer_id)
            
            # Create payment intent (for one-time payment before auto-subscription)
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='ngn',
                customer=customer.id,
                metadata={
                    'school_id': school.id,
                    'tier_id': tier.id,
                    'payment_frequency': payment_frequency,
                }
            )
            
            return Response({
                'status': 'success',
                'client_secret': intent.client_secret,
                'amount': float(amount),
                'tier': tier.display_name,
                'payment_frequency': payment_frequency,
                'discount_applied': f"{discount_percentage}%" if discount_percentage > 0 else "None",
                'next_steps': [
                    'Complete payment on frontend using client_secret',
                    'After payment, subscription will be activated automatically',
                    'You will receive confirmation email'
                ]
            })
        
        except stripe.error.CardError as e:
            logger.error(f"Card error for school {school.id}: {str(e)}")
            return Response(
                {'error': 'Card error: ' + str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Stripe error for school {school.id}: {str(e)}")
            return Response(
                {'error': 'Payment processing error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StripeWebhookView(APIView):
    """Handle Stripe webhooks"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Process webhook events"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle events
        if event['type'] == 'payment_intent.succeeded':
            self.handle_payment_succeeded(event['data']['object'])
        
        elif event['type'] == 'payment_intent.payment_failed':
            self.handle_payment_failed(event['data']['object'])
        
        elif event['type'] == 'customer.subscription.updated':
            self.handle_subscription_updated(event['data']['object'])
        
        elif event['type'] == 'customer.subscription.deleted':
            self.handle_subscription_deleted(event['data']['object'])
        
        return Response({'status': 'success'})
    
    def handle_payment_succeeded(self, payment_intent):
        """Payment completed successfully"""
        school_id = payment_intent.get('metadata', {}).get('school_id')
        tier_id = payment_intent.get('metadata', {}).get('tier_id')
        frequency = payment_intent.get('metadata', {}).get('payment_frequency', 'monthly')
        
        try:
            school = School.objects.get(id=school_id)
            tier = SubscriptionTier.objects.get(id=tier_id)
            
            # Create subscription
            subscription = Subscription.objects.filter(school=school).first()
            if not subscription:
                subscription = Subscription.objects.create(
                    school=school,
                    tier=tier,
                    monthly_price=tier.monthly_price,
                    payment_frequency=frequency,
                    status='active',
                    renewal_date=timezone.now() + timedelta(days=30),
                    stripe_customer_id=payment_intent.get('customer')
                )
            else:
                subscription.status = 'active'
                subscription.tier = tier
                subscription.save()
            
            # Record transaction
            PaymentTransaction.objects.create(
                subscription=subscription,
                amount=payment_intent.get('amount') / 100,  # Convert from cents
                payment_method='card',
                status='completed',
                transaction_id=payment_intent.get('id'),
                stripe_charge_id=payment_intent.get('charges', {}).get('data', [{}])[0].get('id'),
                notes=f"Paid for {frequency} {tier.display_name}"
            )
            
            # Send confirmation email
            self.send_subscription_confirmation_email(school, subscription)
            
            logger.info(f"Payment succeeded for school {school.id}")
        
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
    
    def handle_payment_failed(self, payment_intent):
        """Payment failed"""
        school_id = payment_intent.get('metadata', {}).get('school_id')
        
        try:
            school = School.objects.get(id=school_id)
            subscription = Subscription.objects.filter(school=school).first()
            
            if subscription:
                subscription.status = 'past_due'
                subscription.save()
                
                # Create alert
                BillingAlert.objects.create(
                    subscription=subscription,
                    alert_type='payment_failed',
                    message=f"Payment failed: {payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')}"
                )
            
            logger.warning(f"Payment failed for school {school.id}")
        except Exception as e:
            logger.error(f"Error handling failed payment: {str(e)}")
    
    def handle_subscription_updated(self, stripe_subscription):
        """Subscription updated"""
        customer_id = stripe_subscription.get('customer')
        try:
            subscription = Subscription.objects.get(stripe_customer_id=customer_id)
            subscription.stripe_subscription_id = stripe_subscription.get('id')
            subscription.save()
        except Subscription.DoesNotExist:
            pass
    
    def handle_subscription_deleted(self, stripe_subscription):
        """Subscription cancelled"""
        customer_id = stripe_subscription.get('customer')
        try:
            subscription = Subscription.objects.get(stripe_customer_id=customer_id)
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
        except Subscription.DoesNotExist:
            pass
    
    def send_subscription_confirmation_email(self, school, subscription):
        """Send welcome email after payment"""
        # TODO: Integrate with email service
        logger.info(f"Would send confirmation email to {school.email}")


class UpgradeDowngradeView(APIView):
    """Handle tier changes"""
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def post(self, request):
        """
        Upgrade or downgrade subscription
        
        Body:
        {
            "new_tier_id": 2,
            "effective_date": "immediate" or "next_billing"
        }
        """
        school = request.user.school
        new_tier_id = request.data.get('new_tier_id')
        effective_date = request.data.get('effective_date', 'immediate')
        
        try:
            subscription = Subscription.objects.get(school=school)
            new_tier = SubscriptionTier.objects.get(id=new_tier_id)
        except Subscription.DoesNotExist:
            return Response({'error': 'No active subscription'}, status=404)
        except SubscriptionTier.DoesNotExist:
            return Response({'error': 'Tier not found'}, status=404)
        
        old_tier = subscription.tier
        
        # Calculate proration
        if effective_date == 'immediate':
            now = timezone.now()
            days_remaining = (subscription.renewal_date - now).days
            
            old_daily_rate = float(old_tier.monthly_price) / 30
            new_daily_rate = float(new_tier.monthly_price) / 30
            
            proration_credit = old_daily_rate * days_remaining
            proration_charge = new_daily_rate * days_remaining
            prorated_amount = proration_charge - proration_credit
            
            subscription.tier = new_tier
            subscription.monthly_price = new_tier.monthly_price
            subscription.save()
            
            # TODO: Charge/credit via Stripe
            
            return Response({
                'status': 'success',
                'message': 'Tier upgraded immediately',
                'old_tier': old_tier.display_name,
                'new_tier': new_tier.display_name,
                'prorated_amount': float(prorated_amount),
                'next_billing_cycle': subscription.renewal_date.date()
            })
        
        else:  # next_billing
            # Schedule for next renewal
            BillingAlert.objects.create(
                subscription=subscription,
                alert_type='upgrade_suggested',
                message=f"Tier change from {old_tier.display_name} to {new_tier.display_name} scheduled for {subscription.renewal_date.date()}"
            )
            
            return Response({
                'status': 'scheduled',
                'message': f'Tier will change to {new_tier.display_name} on next renewal',
                'renewal_date': subscription.renewal_date.date()
            })


class CancelSubscriptionView(APIView):
    """Cancel subscription"""
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def post(self, request):
        """Cancel subscription"""
        school = request.user.school
        reason = request.data.get('reason', 'No reason provided')
        
        try:
            subscription = Subscription.objects.get(school=school)
            
            # Cancel with Stripe if exists
            if subscription.stripe_subscription_id:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            
            # Mark as cancelled
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            
            # Downgrade to free tier
            free_tier = SubscriptionTier.objects.get(name='free')
            free_plan, created = FreeSchoolPlan.objects.get_or_create(school=school)
            
            logger.info(f"School {school.id} cancelled subscription. Reason: {reason}")
            
            return Response({
                'status': 'success',
                'message': 'Subscription cancelled. Downgraded to free tier.',
                'remaining_access': 'Until ' + subscription.cancelled_at.strftime('%Y-%m-%d'),
                'free_tier_info': {
                    'max_students': free_tier.max_students,
                    'features': list(FeatureAccess.objects.filter(tier=free_tier, is_enabled=True).values_list('feature', flat=True))
                }
            })
        
        except Subscription.DoesNotExist:
            return Response({'error': 'No active subscription'}, status=404)
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return Response({'error': 'Cancellation failed'}, status=500)


class PaymentHistoryView(APIView):
    """View payment history"""
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def get(self, request):
        """Get school's payment history"""
        school = request.user.school
        try:
            subscription = Subscription.objects.get(school=school)
            transactions = PaymentTransaction.objects.filter(subscription=subscription).order_by('-created_at')
            
            serializer = PaymentTransactionSerializer(transactions, many=True)
            
            # Summary stats
            total_paid = sum(t.amount for t in transactions if t.status == 'completed')
            total_failed = sum(t.amount for t in transactions if t.status == 'failed')
            
            return Response({
                'transactions': serializer.data,
                'summary': {
                    'total_paid': float(total_paid),
                    'total_failed': float(total_failed),
                    'total_transactions': transactions.count(),
                    'completed_transactions': transactions.filter(status='completed').count(),
                }
            })
        except Subscription.DoesNotExist:
            return Response({'error': 'No subscription'}, status=404)


class InvoiceView(APIView):
    """Download invoices"""
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def get(self, request, invoice_id=None):
        """Get invoice or invoice list"""
        school = request.user.school
        
        try:
            subscription = Subscription.objects.get(school=school)
            
            if invoice_id:
                invoice = Invoice.objects.get(id=invoice_id, subscription=subscription)
                # TODO: Return PDF or invoice data
                return Response({
                    'invoice_number': invoice.invoice_number,
                    'amount': float(invoice.amount),
                    'issued_at': invoice.issued_at,
                    'due_at': invoice.due_at,
                    'status': invoice.status,
                })
            else:
                invoices = Invoice.objects.filter(subscription=subscription).order_by('-issued_at')
                serializer = InvoiceSerializer(invoices, many=True)
                return Response(serializer.data)
        
        except Subscription.DoesNotExist:
            return Response({'error': 'No subscription'}, status=404)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=404)
