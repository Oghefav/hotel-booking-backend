from rest_framework import serializers
from custom_user.models import User
from abstract.api.serializers import AbstractModelSerializer

class CustomUserSerializer(serializers.ModelSerializer, AbstractModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = User
        fields = ['public_id', 'email', 'first_name', 'last_name', 'phone', 'username', 'is_active','created_at', 'updated_at',]