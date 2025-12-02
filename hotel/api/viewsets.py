from rest_framework import viewsets
from hotel.models import Hotel, Room, HotelImage, RoomImage
from hotel.api.serializers import HotelSerializer, RoomSerializer, HotelImageSerializer, RoomImageSerializer, UploadHotelImageSerializer, UploadRoomImageSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser,FormParser
import hashlib
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
    

class HotelImagesViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UploadHotelImageSerializer
        return HotelImageSerializer
    
    def get_queryset(self):
        qs = HotelImage.objects.all()
        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='hotel_id',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name='hotel_images',
                in_=openapi.IN_FORM,
                required=True,
                type=openapi.TYPE_FILE,
                description="Select multiple images (Swagger supports one file at a time; use Postman for multiple files)",
            ),
        ],
        responses={201: "Images uploaded successfully"}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        files = request.FILES.getlist('hotel_images')
        print(f" files {files}")
        hotel_id = serializer.validated_data['hotel_id']

        if not files:
            return Response({'message':'No files uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        duplicate_files=[]
        for file in files:
            hasher = hashlib.md5()
            for chunk in file.chunks():
                hasher.update(chunk)
            file_hash = hasher.hexdigest()
            if HotelImage.objects.filter(file_hash=file_hash).exists():
                duplicate_files.append(file.name)
        if duplicate_files:
            return Response({'message':f"Duplicate files {','. join(duplicate_files)}"}, status=status.HTTP_400_BAD_REQUEST)
        # process images here
        try:
            for file in files:
                HotelImage.objects.create(hotel=hotel_id, hotel_image=file)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "ok", 'data':serializer.data}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
               manual_parameters=[
            openapi.Parameter(
                'public_id', openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Hotel public id'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_hotel_images(self, request):
        public_id = request.query_params.get('public_id')

        if not public_id:
            return Response({'message':'public_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try: 
            hotel = Hotel.objects.get(public_id=public_id)
        except Hotel.DoesNotExist:
            return Response({'message':'Invalid public id'}, status=status.HTTP_400_BAD_REQUEST)
        hotel_images = hotel.images.all()
        if not hotel_images:
            return Response({'message':f"{hotel.name} has no images"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = HotelImageSerializer(hotel_images, many=True)

        return Response(serializer.data)
    
    
class RoomImagesViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UploadRoomImageSerializer
        return RoomImageSerializer
    
    def get_queryset(self):
        qs = RoomImage.objects.all()
        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='room_id',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name='room_images',
                in_=openapi.IN_FORM,
                required=True,
                type=openapi.TYPE_FILE,
                description="Select multiple images (Swagger supports one file at a time; use Postman for multiple files)",
            ),
        ],
        responses={201: "Images uploaded successfully"}
    )
    def create(self, request, *args, **kwargs):
        serializer =self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        files = request.FILES.getlist('room_images')
        room_id = serializer.validated_data['room_id']

        # process images here
        if not files:
            return Response({'message':'No files uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        duplicate_files=[]
        for file in files:
            hasher = hashlib.md5()
            for chunk in file.chunks():
                hasher.update(chunk)
            file_hash = hasher.hexdigest()
            if RoomImage.objects.filter(file_hash=file_hash).exists():
                duplicate_files.append(file.name)
        if duplicate_files:
            return Response({'message':f"Duplicate files {','. join(duplicate_files)}"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            for image in files:
                RoomImage.objects.create(room=room_id, room_image=image)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "ok", 'data':serializer.data}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
               manual_parameters=[
            openapi.Parameter(
                'room_id', openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_room_images(self, request):
        room_id = request.query_params.get('room_id')

        if not room_id:
            return Response({'message':'room id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try: 
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return Response({'message':'Invalid room id'}, status=status.HTTP_400_BAD_REQUEST)
        room_images = room.images.all()
        if not room_images:
            return Response({'message':f"{room.room_id} has no images"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoomImageSerializer(room_images, many=True)

        return Response(serializer.data)
