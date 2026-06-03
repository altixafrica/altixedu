"""
Payment API endpoints for Flutterwave integration
Handles payment link creation, verification, and recording
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.finance.models import StudentFee, PaymentReceipt
from apps.finance.serializers import PaymentReceiptSerializer
from apps.finance.flutterwave import get_payment_processor
from apps.core.models import AuditLog


class PaymentViewSet(viewsets.ViewSet):
    """
    Payment management endpoints
    Handles Flutterwave payment links, verification, and recording
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_access_student_fee(user, student_fee):
        if user.role == 'superadmin':
            return True
        if user.role in ['admin', 'bursar']:
            return user.school_id == student_fee.student.school_id
        if user.role == 'student':
            return student_fee.student.user_id == user.id
        if user.role == 'parent':
            return student_fee.student.parent_links.filter(parent=user, is_active=True).exists()
        return False
    
    @action(detail=False, methods=['post'], url_path='initiate-payment')
    def initiate_payment(self, request):
        """
        Create a Flutterwave payment link for a student fee
        
        POST /api/payments/initiate-payment/
        {
            'student_fee_id': 123
        }
        
        Returns:
        {
            'success': True,
            'payment_link': 'https://checkout.flutterwave.com/...',
            'reference': 'ALTIX-1-123-...'
        }
        """
        student_fee_id = request.data.get('student_fee_id')
        if not student_fee_id:
            return Response(
                {'error': 'student_fee_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get student fee (with school context)
            student_fee = get_object_or_404(
                StudentFee.objects.select_related('student', 'student__school', 'student__user', 'fee'),
                id=student_fee_id
            )
            school = student_fee.student.school
            
            # Check permissions - students/parents for their own records, or school finance staff.
            if not self._can_access_student_fee(request.user, student_fee):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create payment link
            processor = get_payment_processor()
            result = processor.create_payment_link(student_fee, school)
            
            if not result['success']:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log payment initiation
            AuditLog.log_change(
                user=request.user,
                instance=student_fee,
                action='payment',
                changes={'payment_initiated': [False, True]},
                school=school,
                ip_address=self._get_client_ip(request),
            )
            
            return Response({
                'success': True,
                'payment_link': result['payment_link'],
                'reference': result['reference'],
                'amount': result['amount'],
                'currency': result['currency'],
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='verify-payment')
    def verify_payment(self, request):
        """
        Verify a payment and record it
        
        POST /api/payments/verify-payment/
        {
            'reference': 'ALTIX-1-123-...',
            'transaction_id': 'optional flutterwave tx id',
            'student_fee_id': 123
        }
        """
        reference = request.data.get('reference')
        student_fee_id = request.data.get('student_fee_id')
        
        if not (reference or student_fee_id):
            return Response(
                {'error': 'reference or student_fee_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get student fee
            student_fee = get_object_or_404(
                StudentFee.objects.select_related('student', 'student__school', 'fee'),
                id=student_fee_id
            )
            school = student_fee.student.school

            if not self._can_access_student_fee(request.user, student_fee):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verify with Flutterwave
            processor = get_payment_processor()
            verification = processor.verify_by_reference(reference)
            
            if not verification['success']:
                return Response(
                    {'error': verification['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Record payment
            result = processor.record_payment(student_fee, verification, request.user, school)
            
            if not result['success']:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Return receipt
            receipt = result['receipt']
            serializer = PaymentReceiptSerializer(receipt)
            
            return Response({
                'success': True,
                'message': 'Payment recorded successfully',
                'receipt': serializer.data,
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='payment-status')
    def payment_status(self, request):
        """
        Check payment status by reference
        
        GET /api/payments/payment-status/?reference=ALTIX-1-123-...
        """
        reference = request.query_params.get('reference')
        if not reference:
            return Response(
                {'error': 'reference required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            processor = get_payment_processor()
            result = processor.verify_by_reference(reference)
            
            if not result['success']:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'reference': reference,
                'status': result['status'],
                'amount': result['amount'],
                'currency': result['currency'],
                'payment_method': result['payment_method'],
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def receipts(self, request):
        """
        List all payment receipts for a student
        
        GET /api/payments/receipts/?student_id=123
        """
        student_id = request.query_params.get('student_id')
        
        if request.user.role == 'student':
            # Students see only their own receipts
            receipts = PaymentReceipt.objects.filter(
                student__user=request.user
            ).order_by('-payment_date')
        elif student_id and request.user.role in ['bursar', 'admin']:
            # Staff can see specific student receipts
            receipts = PaymentReceipt.objects.filter(
                student_id=student_id,
                school=request.user.school
            ).order_by('-payment_date')
        else:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PaymentReceiptSerializer(receipts, many=True)
        return Response({
            'count': receipts.count(),
            'receipts': serializer.data,
        })
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
