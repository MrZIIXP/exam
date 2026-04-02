from django.urls import path
from .views import AddAiQuestion, DeleteChatView
urlpatterns = [
	path('ai/add/', AddAiQuestion.as_view(), name='add_question'),
   path('ai/delete/<int:message_id>/', DeleteChatView.as_view(), name='delete_message'),

]