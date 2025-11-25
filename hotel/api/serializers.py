from rest_framework import serializers
from abstract.models import AbstractModel
from hotel.models import Hotel, Room
import random
class HotelSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Hotel
        fields = ['public_id', 'name', 'city', 'country', 'amenities', 'description', 'created_at', 'updated_at']


    

class RoomSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    room_id = serializers.CharField(read_only=True)
    hotel = serializers.StringRelatedField(read_only=True)
    hotel_id = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all(), source='hotel', write_only=True)
    class Meta:
        model = Room
        fields = [ 'hotel', 'room_id', 'hotel_id','room_type', 'price', 'is_available', 'features', 'created_at', 'updated_at']

    def create(self, validated_data):
        hotel = validated_data['hotel']
        code = random.randint(100000, 300000)
        validated_data['room_id'] = hotel.name[:5].upper() + str(code)
        return Room.objects.create(**validated_data)