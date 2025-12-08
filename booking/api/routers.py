from rest_framework import routers
from booking.api.viewsets import BookingViewSet

router = routers.DefaultRouter()
router.register(r'booking', BookingViewSet, basename='booking')

urlpatterns = [
    *router.urls   
    ]