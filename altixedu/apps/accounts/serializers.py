from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'school'
        ]
        read_only_fields = ['school']  # School auto-set by admin


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating users with password."""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create user with encrypted password."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user, changing password if provided."""
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class CreateMinistryAdminSerializer(serializers.Serializer):
    """Serializer for creating ministry admin - Super Admin only."""
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    country = serializers.CharField(max_length=100, help_text="e.g., Nigeria, Kenya, Ghana")
    state_or_province = serializers.CharField(max_length=100, help_text="e.g., Lagos, Nairobi, Accra")
    
    def validate(self, data):
        """Check if ministry exists for this country/state."""
        from apps.schools.models import Ministry
        try:
            ministry = Ministry.objects.get(
                country=data['country'],
                state_or_province=data['state_or_province']
            )
        except Ministry.DoesNotExist:
            raise serializers.ValidationError(
                f"Ministry not found for {data['state_or_province']}, {data['country']}. "
                "Please create the ministry first."
            )
        return data
    
    def create(self, validated_data):
        """Create ministry admin user and return token."""
        from apps.schools.models import Ministry
        from rest_framework.authtoken.models import Token
        
        ministry = Ministry.objects.get(
            country=validated_data['country'],
            state_or_province=validated_data['state_or_province']
        )
        
        # Create username from email
        username = validated_data['email'].split('@')[0]
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=username,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            role='ministry_admin',
            ministry=ministry,
            is_active=True
        )
        
        # Create token
        token, _ = Token.objects.get_or_create(user=user)
        
        return {
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
            },
            'role': user.role,
            'ministry': {
                'id': ministry.id,
                'name': ministry.name,
                'country': ministry.country,
                'state_or_province': ministry.state_or_province,
                'currency_code': ministry.currency_code,
            },
            'message': f'Ministry admin created successfully for {ministry.state_or_province}, {ministry.country}'
        }


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset."""
    email = serializers.EmailField()
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, min_length=8)
    is_admin_reset = serializers.BooleanField(default=False, help_text="True if super admin is resetting")
    
    def validate(self, data):
        """Validate that user exists and old password is correct (if not admin reset)."""
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email not found.")
        
        # If not admin reset, require old password verification
        if not data.get('is_admin_reset') and data.get('old_password'):
            if not user.check_password(data['old_password']):
                raise serializers.ValidationError("Old password is incorrect.")
        
        data['user'] = user
        return data


class MinistryAdminLoginSerializer(serializers.Serializer):
    """Serializer for ministry admin login - returns state/country data."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate ministry admin credentials."""
        try:
            user = User.objects.get(email=data['email'], role='ministry_admin')
        except User.DoesNotExist:
            raise serializers.ValidationError("Ministry admin with this email not found.")
        
        if not user.check_password(data['password']):
            raise serializers.ValidationError("Invalid password.")
        
        data['user'] = user
        return data
    
    def to_representation(self, instance):
        """Return ministry-specific login data."""
        from rest_framework.authtoken.models import Token
        user = instance['user']
        token, _ = Token.objects.get_or_create(user=user)
        
        return {
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
            },
            'role': 'ministry_admin',
            'ministry': {
                'id': user.ministry.id,
                'name': user.ministry.name,
                'country': user.ministry.country,
                'state_or_province': user.ministry.state_or_province,
                'currency_code': user.ministry.currency_code,
                'currency_symbol': user.ministry.currency_symbol,
            } if user.ministry else None,
            'message': f'Welcome {user.get_full_name()} - Ministry Admin Login Successful'
        }