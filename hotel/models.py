from django.db import models
from abstract.models import AbstractModel

# Create your models here.

class Hotel(AbstractModel):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    amenities = models.JSONField(default=list)  # List of amenities
    description = models.TextField()

    def __str__(self):
        return self.name

class Room(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = 'Single', 'Single'
        DOUBLE = 'Double', 'Double'
        SUITE = 'Suite', 'Suite'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_id = models.CharField(max_length=10, unique=True, primary_key=True, editable=False)
    room_type = models.CharField(max_length=10, choices=RoomType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    features = models.JSONField(default=list)

    def __str__(self):
        return self.room_id