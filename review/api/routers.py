from rest_framework import routers
from review.api.viewsets import AverageRatingViewSet, ReviewViewSet

router = routers.DefaultRouter()

router.register(r'review', ReviewViewSet, basename='review')
router.register(r'average_rating', AverageRatingViewSet, basename='average_rating')

urlpatterns = [
    *router.urls
]