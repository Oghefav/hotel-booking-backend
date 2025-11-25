from rest_framework import routers
from hotel.api.viewsets import HotelViewSet, RoomViewSet

router = routers.DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = [
    *router.urls
]