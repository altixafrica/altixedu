from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
import csv
from .models import Fee, StudentFee
from .serializers import FeeSerializer, StudentFeeSerializer


class FeeViewSet(viewsets.ModelViewSet):
    serializer_class = FeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Fee.objects.all()
        elif user.school:
            return Fee.objects.filter(school=user.school)
        return Fee.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role not in ['admin', 'bursar', 'superadmin']:
            raise PermissionDenied('Only school finance staff can create fees.')

        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export fees as CSV"""
        format_type = request.query_params.get('format', 'csv').lower()
        
        if format_type != 'csv':
            return Response(
                {'error': 'Only CSV format is currently supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fees.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Fee ID', 'Fee Name', 'Amount', 'Currency', 'Due Template', 'Status'
        ])
        
        for fee in queryset:
            writer.writerow([
                fee.id,
                fee.name,
                fee.amount,
                fee.get_currency(),
                fee.due_date_template,
                'active' if fee.is_active else 'inactive',
            ])
        
        return response


class StudentFeeViewSet(viewsets.ModelViewSet):
    serializer_class = StudentFeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return StudentFee.objects.all()
        elif user.school:
            return StudentFee.objects.filter(student__school=user.school)
        return StudentFee.objects.none()

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """
        Custom action for bursars to record a payment.
        POST /api/student-fees/{id}/add_payment/
        Body: {"amount": 5000}
        """
        fee_instance = self.get_object()
        user = request.user
        
        # Check permission
        if user.role not in ['bursar', 'admin', 'superadmin']:
            return Response(
                {"detail": "Permission denied. Only bursars can record payments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate amount
        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except (InvalidOperation, TypeError):
            return Response(
                {"detail": "Invalid amount. Must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount <= 0:
            return Response(
                {"detail": "Amount must be greater than 0."},
                status=status.HTTP_400_BAD_REQUEST
            )

        balance = fee_instance.fee.amount - fee_instance.amount_paid
        if amount > balance:
            return Response(
                {"detail": "Payment amount cannot exceed the outstanding balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Record payment
        fee_instance.add_payment(amount, user)
        serializer = self.get_serializer(fee_instance)
        return Response(
            {
                "detail": f"Payment of {amount} recorded successfully.",
                "fee": serializer.data
            },
            status=status.HTTP_200_OK
        )
