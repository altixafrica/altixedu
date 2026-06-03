"""
Flutterwave payment integration for Altix Edu
Supports: African mobile money, card payments, bank transfers
Currencies: KES, UGX, NGN, GHS, ZAR, TZS, ETB, USD
"""

import requests
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from apps.finance.models import StudentFee, PaymentReceipt
from apps.core.models import AuditLog


class FlutterwavePaymentProcessor:
    """
    Handles all Flutterwave payment operations
    Documentation: https://developer.flutterwave.com/docs/integration-guides/payments/rave-pay/
    """
    
    BASE_URL = "https://api.flutterwave.com/v3"
    
    def __init__(self):
        self.api_key = settings.FLUTTERWAVE_SECRET_KEY
        self.public_key = settings.FLUTTERWAVE_PUBLIC_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def create_payment_link(self, student_fee, school):
        """
        Create a Flutterwave payment link for a student fee
        
        Args:
            student_fee: StudentFee instance
            school: School instance
        
        Returns:
            {
                'success': bool,
                'payment_link': str,
                'reference': str,
                'error': str (if failed)
            }
        """
        try:
            # Calculate amount (convert to float for API)
            amount = float(student_fee.fee.amount)
            currency = student_fee.fee.get_currency()
            
            # Create unique reference (idempotency key)
            reference = f"ALTIX-{school.id}-{student_fee.id}-{timezone.now().timestamp()}"
            
            # Prepare payload
            payload = {
                "tx_ref": reference,
                "amount": amount,
                "currency": currency,
                "payment_options": "card,banktransfer,ussd,mobilemoney",  # All payment methods
                "redirect_url": f"{settings.FRONTEND_APP_URL}/payment-confirmation",
                "customer": {
                    "email": student_fee.student.user.email if student_fee.student.user else school.email,
                    "name": (
                        student_fee.student.user.get_full_name()
                        if student_fee.student.user else f"{student_fee.student.first_name} {student_fee.student.last_name}"
                    ),
                    "phone_number": student_fee.student.user.phone if student_fee.student.user else school.phone,
                },
                "customizations": {
                    "title": f"{school.name} - Fee Payment",
                    "description": f"{student_fee.fee.name} for {student_fee.student.first_name} {student_fee.student.last_name}",
                    "logo": school.logo.url if school.logo else "",
                },
                "meta": {
                    "student_id": student_fee.student.id,
                    "student_fee_id": student_fee.id,
                    "school_id": school.id,
                }
            }
            
            # Send request to Flutterwave
            response = requests.post(
                f"{self.BASE_URL}/payments",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'success': True,
                        'payment_link': data['data']['link'],
                        'reference': reference,
                        'amount': amount,
                        'currency': currency,
                    }
            
            return {
                'success': False,
                'error': response.json().get('message', 'Payment link creation failed'),
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def verify_payment(self, transaction_id):
        """
        Verify a payment with Flutterwave using transaction ID
        
        Args:
            transaction_id: Flutterwave transaction ID
        
        Returns:
            {
                'success': bool,
                'status': 'successful'/'failed'/'pending',
                'amount': float,
                'currency': str,
                'reference': str,
                'customer_email': str,
                'payment_method': str,
                'error': str (if failed)
            }
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/transactions/{transaction_id}/verify",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'success': True,
                        'status': data['data']['status'],  # successful/failed/pending
                        'amount': data['data']['amount'],
                        'currency': data['data']['currency'],
                        'reference': data['data']['tx_ref'],
                        'customer_email': data['data']['customer']['email'],
                        'payment_method': data['data']['payment_type'],
                        'flutterwave_id': transaction_id,
                    }
            
            return {
                'success': False,
                'error': response.json().get('message', 'Payment verification failed'),
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def verify_by_reference(self, reference):
        """
        Verify a payment by transaction reference (tx_ref)
        More efficient than using transaction ID
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/transactions/verify_by_reference?tx_ref={reference}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'success': True,
                        'status': data['data']['status'],
                        'amount': data['data']['amount'],
                        'currency': data['data']['currency'],
                        'reference': reference,
                        'customer_email': data['data']['customer']['email'],
                        'payment_method': data['data']['payment_type'],
                        'flutterwave_id': data['data']['id'],
                    }
            
            return {
                'success': False,
                'error': response.json().get('message', 'Payment verification failed'),
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def record_payment(self, student_fee, verification_data, user, school):
        """
        Record a verified payment in the database
        Creates PaymentReceipt and updates StudentFee
        
        Args:
            student_fee: StudentFee instance
            verification_data: Result from verify_payment()
            user: User who recorded the payment
            school: School instance
        
        Returns:
            {
                'success': bool,
                'receipt': PaymentReceipt instance (if successful),
                'error': str (if failed)
            }
        """
        try:
            # Only record if payment is successful
            if verification_data['status'] != 'successful':
                return {
                    'success': False,
                    'error': f"Payment status is {verification_data['status']}, not successful",
                }
            
            # Check if already recorded (idempotency)
            existing = PaymentReceipt.objects.filter(
                student_fee=student_fee,
                receipt_number__contains=verification_data['flutterwave_id']
            ).exists()
            
            if existing:
                return {
                    'success': False,
                    'error': 'Payment already recorded',
                }
            
            # Create receipt
            receipt = PaymentReceipt.objects.create(
                student_fee=student_fee,
                student=student_fee.student,
                school=school,
                receipt_number=f"FLW-{verification_data['flutterwave_id']}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                amount=Decimal(str(verification_data['amount'])),
                currency_code=verification_data['currency'],
                payment_method='flutterwave',
                paid_by=user,
                payment_date=timezone.now(),
            )
            
            # Update StudentFee
            student_fee.add_payment(verification_data['amount'], user)
            
            # Log in audit trail
            AuditLog.log_change(
                user=user,
                instance=receipt,
                action='payment',
                changes={
                    'payment_method': ['manual', 'flutterwave'],
                    'amount': [0, verification_data['amount']],
                },
                school=school,
            )
            
            return {
                'success': True,
                'receipt': receipt,
                'message': f"Payment recorded: {receipt.receipt_number}",
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }


def get_payment_processor():
    """Factory function to get payment processor"""
    return FlutterwavePaymentProcessor()
