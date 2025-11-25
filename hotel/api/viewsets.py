from rest_framework import viewsets
from hotel.models import Hotel, Room
from hotel.api.serializers import HotelSerializer, RoomSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from drf_yasg import openapi
from rest_framework import status
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
    def search(self, request):
        city = request.query_params.get('city')
        country = request.query_params.get('country')

        filters = {}
        if city:
            filters['city'] = city
        if country:
            filters['country'] = country

        hotels = Hotel.objects.filter(**filters)

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
    
    