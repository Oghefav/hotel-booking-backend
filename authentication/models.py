from django.db import models
from  django.utils import timezone
import secrets
from datetime import timedelta
from custom_user.models import User
# Create your models here.

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_code')
    code = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    times_used = models.PositiveIntegerField(default=0)

    @staticmethod
    def create_code(user,):
        code = secrets.token_hex(3)
        expires_at = timezone.now() +  timedelta(minutes=4)
        return VerificationCode.objects.create(
            user = user,
            code = code,
            expires_at = expires_at
        )