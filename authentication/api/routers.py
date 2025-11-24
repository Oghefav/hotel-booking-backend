from rest_framework import routers
from authentication.api.viewsets import CustomerRegistrationViewSet, LoginViewSet, PasswordChangeViewSet, PasswordResetCodeViewSet, PasswordResetViewSet, LogOutViewSet

router = routers.DefaultRouter()
router.register(r'customer-registration', CustomerRegistrationViewSet, basename='customer-registration')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'password-change', PasswordChangeViewSet, basename='password-change')
router.register(r'password-reset-code', PasswordResetCodeViewSet, basename='password-reset-code')
router.register(r'reset-password', PasswordResetViewSet, basename='reset-password')
router.register(r'logout', LogOutViewSet, basename='logout')

urlpatterns = [
    *router.urls,
    ]