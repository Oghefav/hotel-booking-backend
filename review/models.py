from django.db import models
from abstract.models import AbstractModel
from custom_user.models import User
from hotel.models import Hotel
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

class Review(AbstractModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])

    class Meta:
        unique_together = ['customer', 'hotel']
        ordering = ['-review']

    def __str__(self):
        return f"{self.customer} commented on {self.hotel}"
    
class AverageRating(models.Model):
    hotel = models.OneToOneField(Hotel, on_delete=models.CASCADE, related_name='average_rating')
    average_rating = models.DecimalField(decimal_places=2, max_digits=5, null=True) 
    total_reviews = models.PositiveIntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.hotel.name} has an average rating of {self.average_rating}"