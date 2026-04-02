from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import secrets
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
   is_verifired = models.BooleanField(default=False)
   email_token = models.CharField(blank=True, null=True)
   email_at = models.DateTimeField(blank=True, null=True)
   reset_password_token = models.CharField(blank=True, null=True)
   reset_password_at = models.DateTimeField(blank=True, null=True)

   def email_send_token(self):
      self.email_token = secrets.token_urlsafe(8)
      self.email_at = timezone.now()
      self.save()
   
   def email_token_is_valid(self):
      if not self.email_token:
         return False
      elif not self.email_at:
         return False
      elif self.email_at + timedelta(minutes=5) < timezone.now():
         return False
      return timezone.now() <= self.email_at + timedelta(minutes=5)
   
   def confirm_email_token(self):
      self.is_verifired = True
      self.email_token = None
      self.email_at = None
      self.save()
   
   
   def reset_password_send_token(self):
      self.reset_password_token = secrets.token_urlsafe(8)
      self.reset_password_at = timezone.now()
      self.save()
   
   def reset_password_token_is_valid(self):
      if not self.reset_password_token:
         return False
      elif not self.reset_password_at:
         return False
      elif self.reset_password_at + timedelta(minutes=5) < timezone.now():
         return False
      return timezone.now() <= self.reset_password_at + timedelta(minutes=5)
   
   def confirm_reset_password_token(self):
      self.reset_password_at = None
      self.reset_password_token = None
      self.save()
   
   def __str__(self):
      return self.username


class Profile(models.Model):
   avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
   phone = models.CharField(max_length=13, blank=True, null=True)
   user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

   def avg_rating(self):
      result = self.user.reviews.aggregate(avg=models.Avg('rating'))
      return result['avg'] or 0

   def __str__(self):
      return f'{self.user.username} - {self.phone}'