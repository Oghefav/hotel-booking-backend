from django.db import models
from abstract.models import AbstractModel
import hashlib

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
    room_id = models.CharField(max_length=15, unique=True, primary_key=True, editable=False)
    room_type = models.CharField(max_length=10, choices=RoomType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    features = models.JSONField(default=list)

    def __str__(self):
        return self.room_id
    
class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    hotel_image = models.ImageField(upload_to='hotel_images', )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=100, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.hotel_image and not self.file_hash:
            self.hotel_image.seek(0)
            hasher = hashlib.md5()
            for chunk in self.hotel_image.chunks():
                hasher.update(chunk)
            self.file_hash = hasher.hexdigest()
            self.hotel_image.seek(0)
        super().save(*args, **kwargs)

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    room_image = models.ImageField(upload_to='room_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=100, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.room_image and not self.file_hash:
            self.room_image.seek(0)
            hasher = hashlib.md5()
            for chunk in self.room_image.chunks():
                hasher.update(chunk)
            self.file_hash = hasher.hexdigest()
            self.room_image.seek(0)
        super().save(*args, **kwargs)