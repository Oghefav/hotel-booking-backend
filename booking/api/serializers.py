from rest_framework import serializers
from booking.models import Booking
from hotel.models import Hotel,Room
from custom_user.models import User
from abstract.api.serializers import AbstractModelSerializer
from django.db.models import Max
from datetime import timedelta

def get_next_available_date(room,):
    lastest_available_date = Booking.objects.filter(room=room).aggregate(last_check_out=Max('check_out'))['last_check_out']

    if not lastest_available_date:
        return None
    return lastest_available_date + timedelta(days=1), 'it will be avaliable from'

class BookingSerializer(serializers.ModelSerializer, AbstractModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='customer', write_only=True)
    hotel = serializers.StringRelatedField(read_only=True)
    hotel_id = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all(), source='hotel', write_only=True)
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2,read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), source='room', write_only=True)
    room = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = ['public_id', 'created_at', 'updated_at' ,'customer', 'hotel','customer_id', 'hotel_id','room_id' ,'room', 'check_in', 'check_out', 'status', 'total_price',]

    def create(self, validated_data):
        room = validated_data['room']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        days = (check_out - check_in).days
        if days == 0:
            days = 1
        validated_data['total_price'] = room.price * days
        return Booking.objects.create(**validated_data)
    
    def validate(self, attrs):
        room = attrs.get('room')
        new_check_in = attrs.get('check_in')
        new_check_out = attrs.get('check_out')
        overlapping_bookings = Booking.objects.filter(
            room=room,
            check_in__lt=new_check_out,
            check_out__gte=new_check_in,
            # status = 'Confirmed'
        ).exists()
        last_available_date, msg = get_next_available_date(room)
        if overlapping_bookings:
            raise serializers.ValidationError(f"The room is already booked for the selected dates. {msg} {last_available_date}")
        return attrs