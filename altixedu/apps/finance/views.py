from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
        if self.request.user.school:
            serializer.save(school=self.request.user.school)
        else:
            serializer.save()


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
        if user.role not in ['bursar', 'superadmin', 'schooladmin']:
            return Response(
                {"detail": "Permission denied. Only bursars can record payments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate amount
        try:
            amount = float(request.data.get('amount', 0))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid amount. Must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount <= 0:
            return Response(
                {"detail": "Amount must be greater than 0."},
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
