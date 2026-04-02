from django.urls import path
from .views import *
urlpatterns = [
	path('', CatalogView.as_view(), name='catalog'),
	path('<int:pk>/', CatalogDetail.as_view(), name='car_detail'),
	path('car/<int:pk>/send-message/', SendMessageView.as_view(), name='send_message'),
]