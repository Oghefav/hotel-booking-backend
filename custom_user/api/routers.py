from rest_framework import routers
from custom_user.api.viewset import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    *router.urls,
]