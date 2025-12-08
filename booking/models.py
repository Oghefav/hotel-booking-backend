from django.db import models
from abstract.models import AbstractModel
from django.conf import settings
from hotel.models import Room, Hotel
# Create your models here.
class Booking(AbstractModel):
    class BookingStatus(models.TextChoices):
        FAILED = 'Failed', 'Failed'
        CONFIRMED = 'Confirmed', 'Confirmed'
        CANCELLED = 'Cancelled', 'Cancelled'
        PENDING = 'Pending', 'Pending'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, related_name='bookings', null=True)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=10, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('room', 'check_in', 'check_out')

    def __str__(self):
        return f'Booking {self.public_id} - {self.customer.username} - {self.room.room_id}'
