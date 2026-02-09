from rest_framework import serializers
from custom_user.api.serializers import CustomUserSerializer
from custom_user.models import User
from abstract.api.serializers import AbstractModelSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password as django_validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login

class CustomerRegistrationSerializer(serializers.ModelSerializer, AbstractModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['public_id','email', 'first_name', 'last_name', 'phone',  'password', 'confirm_password', 'public_id', 'created_at', 'updated_at', 'is_active',] 

    def create(self, validated_data):
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def validate_password(self, value):
        try:
            django_validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        return value
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    
class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh_token = self.get_token(self.user)

        data['user'] = CustomUserSerializer(self.user).data
        data['refresh'] = str(refresh_token)
        data['access'] = str(refresh_token.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
    
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        try:
            django_validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
class PasswordResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    reset_code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)