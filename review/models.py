from django.db import models
from django.conf import settings


class Review(models.Model):
   from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
   text = models.TextField()
   rating = models.PositiveSmallIntegerField()
   created_at = models.DateTimeField(auto_now_add=True)
   
   def __str__(self):
      return self.text
   
   class Meta:
      permissions = [
         ('can_add_review', 'Can add review'),
         ('can_delete_review', 'Can delete review'),
         ('can_delete_any_review', 'Can delete any review')
      ]