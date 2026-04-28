from rest_framework import serializers

from .models import Ministry, School


class MinistrySerializer(serializers.ModelSerializer):
    school_count = serializers.SerializerMethodField()
    active_school_count = serializers.SerializerMethodField()
    trial_school_count = serializers.SerializerMethodField()
    billable_school_count = serializers.SerializerMethodField()

    class Meta:
        model = Ministry
        fields = [
            'id',
            'name',
            'country',
            'state_or_province',
            'state',
            'contact_email',
            'contact_phone',
            'address',
            'currency_code',
            'currency_symbol',
            'school_count',
            'active_school_count',
            'trial_school_count',
            'billable_school_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'school_count',
            'active_school_count',
            'trial_school_count',
            'billable_school_count',
        ]

    def get_school_count(self, obj):
        return obj.schools.count()

    def get_active_school_count(self, obj):
        return obj.schools.filter(subscription__status='active').count()

    def get_trial_school_count(self, obj):
        return obj.schools.filter(subscription__status='trial').count()

    def get_billable_school_count(self, obj):
        return obj.schools.filter(subscription__isnull=False).exclude(subscription__tier__name='free').count()


class SchoolSerializer(serializers.ModelSerializer):
    """Full CRUD serializer for schools"""
    ministry_name = serializers.CharField(source='ministry.name', read_only=True, allow_null=True)
    subscription_status = serializers.CharField(
        source='subscription.status',
        read_only=True,
        allow_null=True,
    )
    subscription_tier = serializers.CharField(
        source='subscription.tier.display_name',
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'subdomain',
            'email',
            'phone',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
            'website',
            'logo',
            'primary_color',
            'secondary_color',
            'timezone',
            'language',
            'school_type',
            'region',
            'ministry',
            'ministry_name',
            'subscription_status',
            'subscription_tier',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'ministry_name', 'subscription_status', 'subscription_tier']


class SchoolDirectorySerializer(serializers.ModelSerializer):
    full_domain = serializers.CharField(read_only=True)
    ministry_name = serializers.CharField(source='ministry.name', read_only=True, allow_null=True)
    ministry_state = serializers.CharField(
        source='ministry.state_or_province',
        read_only=True,
        allow_null=True,
    )
    subscription_status = serializers.CharField(
        source='subscription.status',
        read_only=True,
        allow_null=True,
    )
    subscription_tier = serializers.CharField(
        source='subscription.tier.display_name',
        read_only=True,
        allow_null=True,
    )
    subscription_frequency = serializers.CharField(
        source='subscription.payment_frequency',
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'subdomain',
            'full_domain',
            'email',
            'phone',
            'city',
            'state',
            'country',
            'website',
            'timezone',
            'language',
            'school_type',
            'region',
            'ministry',
            'ministry_name',
            'ministry_state',
            'subscription_status',
            'subscription_tier',
            'subscription_frequency',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'full_domain']
