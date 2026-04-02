from django.db import models
from django.conf import settings

class CarManage(models.Manager):
   def get_queryset(self):
      return super().get_queryset().filter(is_deleted=False)

class AllCarManage(models.Manager):
   def get_queryset(self):
      return super().get_queryset()

class Brand(models.Model):
   name = models.CharField(max_length=100)
   image = models.ImageField(upload_to='brand/')
   def __str__(self):
      return self.name
   
   class Meta:
      permissions = [
         ('can_manage_brands', 'Can manage brands')
      ]


class BodyStyle(models.Model):
   name = models.CharField(max_length=100)
   image = models.ImageField(upload_to='brand/')
   def __str__(self):
      return self.name

   class Meta:
      permissions = [
         ('can_manage_body_style', 'Can manage Body Style')
      ]

class Transmission(models.Model):
   name = models.CharField(max_length=150)
   def __str__(self):
      return self.name

   class Meta:
      permissions = [
         ('can_manage_transmission', 'Can manage transmission')
      ]



class Car(models.Model):
   brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='car')
   body_style = models.ForeignKey(BodyStyle, on_delete=models.CASCADE, related_name='car')
   transmission = models.ForeignKey(Transmission, on_delete=models.CASCADE, related_name='car')
   user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='car')
   is_deleted = models.BooleanField(default=False)
   speed = models.PositiveIntegerField()
   title = models.CharField(max_length=100)
   description = models.TextField(null=True, blank=True)
   price = models.DecimalField(max_digits=10, decimal_places=2)
   created_at = models.DateField(auto_now_add=True)
   
   all_cars = AllCarManage()
   objects = CarManage()
   
   image_1 = models.ImageField(upload_to='car_images/')
   image_2 = models.ImageField(upload_to='car_images/', blank=True, null=True)
   image_3 = models.ImageField(upload_to='car_images/', blank=True, null=True)
   image_4 = models.ImageField(upload_to='car_images/', blank=True, null=True)

   def soft_delete(self):
      self.is_deleted = True
      self.save(update_fields=['is_deleted'])
   
   def restore(self):
      self.is_deleted = False
      self.save(update_fields=['is_deleted'])
   
   def __str__(self):
      return f'{self.title} - {self.price} - {self.user.first_name}. {self.created_at}'

   class Meta:
      permissions = [
         ('can_add_car', 'Can add car'),
         ('can_edit_car', 'Can edit car'),
         ('can_edit_any_car', 'Can edit any car'),
         ('can_delete_car', 'Can delete car'),
         ('can_delete_any_car', 'Can delete any car')
      ]
      
      
      