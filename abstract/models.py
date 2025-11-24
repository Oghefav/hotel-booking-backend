from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import uuid
from django.http import Http404
# Create your models here.

class AbstractManager(models.Manager):
    def get_by_public_id(self, public_id):
        try:
            return self.get(public_id=public_id)
        except (ObjectDoesNotExist, ValueError, Http404):
            raise Http404("Object with the given public_id does not exist.")
        
class AbstractModel(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AbstractManager()

    class Meta:
        abstract = True

