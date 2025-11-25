from rest_framework import viewsets
from booking.models import Booking
from rest_framework.permissions import IsAuthenticated
from booking.api.serializers import BookingSerializer
from rest_framework.response import Response
from rest_framework import status

class BookingViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['check_in'] > serializer.validated_data['check_out']:
            return Response({"error": "Check-out date must be after check-in date."}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)