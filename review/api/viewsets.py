from rest_framework import viewsets
from review.api.serializers import RatingSerializer, AverageRatingSerializer
from rest_framework.response import Response
from rest_framework import status
from review.models import Review, AverageRating
from rest_framework.permissions import IsAuthenticated

class ReviewViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']  
    serializer_class = RatingSerializer 
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        obj = Review.objects.all()
        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)   
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'Review successfully added', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
class AverageRatingViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    serializer_class = AverageRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        obj = AverageRating.objects.all()
        return obj
    