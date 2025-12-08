from rest_framework import serializers
from review.models import AverageRating, Review
from custom_user.models import User
from hotel.models import Hotel
from abstract.api.serializers import AbstractModelSerializer

class AverageRatingSerializer(serializers.ModelSerializer):
    hotel = serializers.StringRelatedField()
    class Meta:
        model = AverageRating
        fields = ['hotel', 'average_rating', 'total_reviews']

class RatingSerializer(serializers.ModelSerializer, AbstractModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='customer')
    hotel = serializers.StringRelatedField(read_only=True)
    hotel_id = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all(), source='hotel', write_only=True)
    class Meta:
        model = Review
        fields = ['public_id','customer','customer_id', 'hotel','hotel_id', 'review', 'rating', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Review.objects.create(**validated_data)
    def validate(self, attrs):
        customer= attrs['customer']
        hotel = attrs['hotel']
        if Review.objects.filter(customer=customer, hotel=hotel).exists():
            raise serializers.ValidationError('This user have reviewed this hotel, multiple reviews are not allowed')
        return super().validate(attrs)
