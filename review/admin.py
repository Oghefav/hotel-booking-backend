from django.contrib import admin
from review.models import Review,AverageRating
# Register your models here.
admin.site.register([Review, AverageRating])
