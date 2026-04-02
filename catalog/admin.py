from django.contrib import admin
from .models import BodyStyle, Brand, Car, Transmission

admin.site.register(BodyStyle)
admin.site.register(Brand)
admin.site.register(Car)
admin.site.register(Transmission)