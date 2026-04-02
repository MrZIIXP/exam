from django.urls import path
from .views import *
urlpatterns = [
	path('', CatalogView.as_view(), name='catalog'),
	path('<int:pk>/', lambda x: x, name='car_detail')
]