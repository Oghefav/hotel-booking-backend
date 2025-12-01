from rest_framework import viewsets
from hotel.models import Hotel, Room
from hotel.api.serializers import HotelSerializer, RoomSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from drf_yasg import openapi
from rest_framework import status
from datetime import datetime
from rest_framework.response import Response
from utility.permissions import isAdminUserOrReadOnly

class HotelViewSet(viewsets.ModelViewSet):
    serializer_class = HotelSerializer
    permission_classes = [isAdminUserOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
# fix lowercase searching
    def get_queryset(self):
        return Hotel.objects.all()
    
    @swagger_auto_schema(
               manual_parameters=[
            openapi.Parameter(
                'city', openapi.IN_QUERY,
                description="Filter by city",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'country', openapi.IN_QUERY,
                description="filter by country",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def search_by_location(self, request):
        city = str(request.query_params.get('city')).lower()
        country = str(request.query_params.get('country')).lower()
        print(city)
        hotels = None
        if city:
            hotels = Hotel.objects.filter(city=city)
        if country:
            hotels = Hotel.objects.filter(country=country)
        if city and country:
            hotels = Hotel.objects.filter(city=city, country=country)

        
        if not hotels.exists():
            # Message handles missing city/country
            if city and country:
                msg = f"No hotel found in {city}, {country}"
            elif city:
                msg = f"No hotel found in {city}"
            elif country:
                msg = f"No hotel found in {country}"
            else:
                msg = "No hotels found"
            return Response({'message': msg}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(hotels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    
class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [isAdminUserOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']

    def get_queryset(self):
        return Room.objects.all()   
    
    @swagger_auto_schema(
               manual_parameters=[
            openapi.Parameter(
                'check_in', openapi.IN_QUERY,
                type=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'check_out', openapi.IN_QUERY,
                type=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'hotel', openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'city', openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'room_type', openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def search_for_avaliable_rooms(self, request):
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        print(f"check in {check_in} check out {check_out}")
        hotel = request.query_params.get('hotel')
        city = request.query_params.get('city')
        print(city)
        room_type = str(request.query_params.get('room_type')).title()

        if not (check_in and check_out and hotel and city and room_type):

            return Response({'message':'Missing required parameters'}, status=400)

        check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out, '%Y-%m-%d').date()

        available_rooms = Room.objects.filter(hotel__name=hotel, hotel__city=city, room_type=room_type).exclude(bookings__check_in__lte=check_out, bookings__check_out__gte=check_in,)
        if available_rooms.exists():
            msg = []
            if Room.objects.filter(bookings__check_in__lt=check_out, bookings__check_out__gt=check_in).exists():
                msg.append(f"No room is available from {check_in} to { check_out}")
            if not Room.objects.filter(hotel__name=hotel,).exists():
                msg.append(f"No room available in {hotel}")
            if not Room.objects.filter(room_type=room_type).exists():
                msg.append(f"No room with room type {room_type} is avaliable in {hotel}, {city}")
            return Response({'message':msg,}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(available_rooms, many=True)
        return Response({'message':serializer.data,}, status=status.HTTP_200_OK)
    
    