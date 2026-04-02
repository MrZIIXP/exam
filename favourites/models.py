from django.db import models
from django.conf import settings
from catalog.models import Car

class Favourite(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favourites')
	car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favourites')
