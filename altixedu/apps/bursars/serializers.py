from rest_framework import serializers
from apps.bursars.models import Bursar


class BursarSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Bursar
        fields = [
            'id',
            'school',
            'school_name',
            'user',
            'user_email',
            'user_name',
            'managed_fees',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
