from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from custom_user.models import User
from custom_user.api.serializers import CustomUserSerializer

class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

   