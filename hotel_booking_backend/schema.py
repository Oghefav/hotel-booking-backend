from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
schema_view = get_schema_view(
    openapi.Info(
        title="Hotel Booking API",
        default_version='v1',
        description="API documentation for the Hotel Booking system",
        contact=openapi.Contact(email="favouroghenevwoke@gmail.com"),
        license=openapi.License(name="Hotel_booking_license"),
        terms_of_service="https://www.google.com/policies/terms/",      
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    )