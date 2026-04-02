from django.db import models
from django.conf import settings
from catalog.models import Car

class Deal(models.Model):
   
   CHOISES = [
		('in_transit', 'In Transit'),
		('processing', 'Processing'),
		('delivered', 'Delivered'),
	]
   
   seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_deal')
   buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deals')
   car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='deals')
   status = models.CharField(choices=CHOISES)