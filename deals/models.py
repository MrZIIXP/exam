from django.db import models
from django.conf import settings
from catalog.models import Car

class Deal(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='selling_deals')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buying_deals')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='deals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.car.title} - {self.status}"