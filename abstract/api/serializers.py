from rest_framework import serializers
from abstract.models import AbstractModel

class AbstractModelSerializer(serializers.Serializer):
    public_id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)  
    updated_at = serializers.DateTimeField(read_only=True)