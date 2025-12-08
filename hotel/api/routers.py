from rest_framework import routers
from hotel.api.viewsets import HotelViewSet, RoomViewSet, RoomImagesViewSet, HotelImagesViewSet

router = routers.DefaultRouter()
router.register(r'hotel', HotelViewSet, basename='hotel')
router.register(r'room', RoomViewSet, basename='room')
router.register(r'room_image', RoomImagesViewSet, basename='room_image')
router.register(r'hotel_image', HotelImagesViewSet, basename='hotel_image')

urlpatterns = [
    *router.urls
]