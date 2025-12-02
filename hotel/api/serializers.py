from rest_framework import serializers
from abstract.models import AbstractModel
from hotel.models import Hotel, Room, HotelImage, RoomImage
import random
class HotelSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Hotel
        fields = ['public_id', 'name', 'city', 'country', 'amenities', 'description', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['name'] = validated_data['name'].lower()
        validated_data['country'] = validated_data['country'].lower()
        return Hotel.objects.create(**validated_data)


    

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
        room=Room(**validated_data)
        room.room_id = hotel.name[:5].upper() + str(code)
        room.save()
        return room
    
class UploadHotelImageSerializer(serializers.Serializer):
    hotel_id = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
#     hotel_images = serializers.ListField(
#     child=serializers.ImageField(),
#     allow_empty=False,
#     help_text="Select multiple images. For Swagger UI, only one can be selected. Use Postman or frontend to upload multiple files."
# )
    

class UploadRoomImageSerializer(serializers.Serializer):
    room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    # room_images = serializers.ListField(child=serializers.ImageField(), allow_empty=False, help_text="Select multiple images. For Swagger UI, only one can be selected. Use Postman or frontend to upload multiple files.")

    

class RoomImageSerializer(serializers.ModelSerializer):
    room = serializers.StringRelatedField(read_only=True)
    
    class  Meta:
        model = RoomImage
        fields = ['id', 'room', 'room_image']

class HotelImageSerializer(serializers.ModelSerializer):
    hotel = serializers.StringRelatedField(read_only=True)
    
    class  Meta:
        model = HotelImage
        fields = ['id', 'hotel', 'hotel_image']