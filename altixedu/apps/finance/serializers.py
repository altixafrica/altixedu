from rest_framework import serializers
from .models import Fee, StudentFee


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = ['id', 'name', 'school', 'amount', 'created_at']
        read_only_fields = ['school']


class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.get_full_name',
        read_only=True
    )
    fee_name = serializers.CharField(
        source='fee.name',
        read_only=True
    )
    recorded_by_name = serializers.CharField(
        source='recorded_by.get_full_name',
        read_only=True
    )
    fee_amount = serializers.FloatField(
        source='fee.amount',
        read_only=True
    )
    amount_remaining = serializers.SerializerMethodField()

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
            'due_date',
            'paid',
            'recorded_by',
            'recorded_by_name',
            'history'
        ]
        read_only_fields = ['history', 'paid', 'recorded_by', 'amount_remaining']

    def get_amount_remaining(self, obj):
        return max(0, obj.fee.amount - obj.amount_paid)