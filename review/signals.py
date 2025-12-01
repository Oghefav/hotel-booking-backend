from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Avg
from review.models import AverageRating, Review

@receiver(post_save, sender=Review)
def update_hotel_rating_on_save(sender, instance, **kwargs):
    hotel = instance.hotel
    reviews = hotel.reviews.all()
    total_reviews = reviews.count()

    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))["avg_rating"] or 0.0
    hotel_ratings, created = AverageRating.objects.get_or_create(hotel=hotel,)
    hotel_ratings.average_rating = avg_rating
    hotel_ratings.total_reviews = total_reviews
    hotel_ratings.save()

@receiver(post_delete, sender=Review)
def update_hotel_rating_on_delete(sender, instance, **kwargs):
    hotel = instance.hotel
    reviews = hotel.reviews.all()
    total_reviews = reviews.count()

    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))["avg_rating"] or 0.0
    hotel_ratings, created = AverageRating.objects.get_or_create(hotel=hotel,)
    hotel_ratings.average_rating = avg_rating
    hotel_ratings.total_reviews = total_reviews
    hotel_ratings.save()
