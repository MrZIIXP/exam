from django.db import models
from django.conf import settings

class AIHistory(models.Model):
   user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='history')
   
   class Meta:
       permissions = [ 
           ('can_view_ai_history', 'Can view ai history'),
           ('can_delete_ai_history', 'Can delete ai history')
       ]
   def __str__(self):
        return f"History {self.id} - {self.user.username}"



class AIRecommendation(models.Model):
    MODE_CHOICES = [
        ('recommendate', 'Recommendate'),
        ('search', 'Search'),
		  ('ask', 'Ask')
    ]
    chat_id = models.ForeignKey(AIHistory, on_delete=models.CASCADE, related_name='messages')
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

