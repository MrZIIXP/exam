from ai.models import AIHistory
from django.http import HttpRequest


def ai(request: HttpRequest):
   history = AIHistory.objects.filter(user__id=request.session.get('user_id')).first()
   content = {}
   if history:
      content['history'] = history
      content['messages'] = history.messages.all()[::-1]
   return content