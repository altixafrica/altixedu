from rest_framework import serializers
from .models import Fee, StudentFee, PaymentReceipt


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = [
            'id',
            'name',
            'school',
            'amount',
            'currency_code',
            'description',
            'due_date_template',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['school']


class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    fee_name = serializers.CharField(
        source='fee.name',
        read_only=True
    )
    recorded_by_name = serializers.CharField(
        source='recorded_by.get_full_name',
        read_only=True
    )
    fee_amount = serializers.DecimalField(
        source='fee.amount',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    amount_remaining = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()

    class Meta:
        model = StudentFee
        fields = [
            'id',
            'student',
            'student_name',
            'fee',
            'fee_name',
            'fee_amount',
            'amount_paid',
            'amount_remaining',
            'balance_due',
            'currency_symbol',
            'due_date',
            'paid',
            'recorded_by',
            'recorded_by_name',
            'history'
        ]
        read_only_fields = ['history', 'paid', 'recorded_by', 'amount_remaining', 'balance_due', 'currency_symbol']

    def get_amount_remaining(self, obj):
        return max(0, obj.fee.amount - obj.amount_paid)
    
    def get_balance_due(self, obj):
        """Get remaining balance"""
        return max(0, obj.fee.amount - obj.amount_paid)
    
    def get_currency_symbol(self, obj):
        """Get school currency symbol"""
        return obj.student.school.currency_symbol if obj.student.school else '$'

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip()


class PaymentReceiptSerializer(serializers.ModelSerializer):
    """Serializer for payment receipts"""
    student_name = serializers.SerializerMethodField()
    fee_name = serializers.CharField(
        source='student_fee.fee.name',
        read_only=True
    )
    paid_by_name = serializers.CharField(
        source='paid_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = PaymentReceipt
        fields = [
            'id',
            'receipt_number',
            'student',
            'student_name',
            'student_fee',
            'fee_name',
            'amount',
            'currency_code',
            'amount_in_usd',
            'payment_method',
            'paid_by',
            'paid_by_name',
            'payment_date',
        ]
        read_only_fields = [
            'id',
            'receipt_number',
            'student_name',
            'fee_name',
            'paid_by_name',
            'payment_date',
        ]

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip()
