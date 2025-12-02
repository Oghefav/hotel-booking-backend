from rest_framework import routers
from hotel.api.viewsets import HotelViewSet, RoomViewSet, RoomImagesViewSet, HotelImagesViewSet

router = routers.DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'room_images', RoomImagesViewSet, basename='room_images')
router.register(r'hotel_images', HotelImagesViewSet, basename='hotel_images')

urlpatterns = [
    *router.urls
]