from django.db import models
from django.conf import settings



class AIRecommendation(models.Model):
    MODE_CHOICES = [
        ('recmomendate', 'Recommendate'),
        ('search', 'Search'),
		  ('ask', 'Ask')
    ]

    title = models.CharField(max_length=200)
    user_text = models.TextField()
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    ai_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.title
    
    class Meta:
        permissions = [
            ('can_ask_ai', 'Can ask AI'),
        ]

class AIHistory(models.Model):
   user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='history')
   chat_id = models.ForeignKey(AIRecommendation, on_delete=models.CASCADE)
   
   class Meta:
       permissions = [
           ('can_view_ai_history', 'Can view ai history'),
           ('can_delete_ai_history', 'Can delete ai history')
       ]