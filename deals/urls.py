from django.urls import path
from .views import *


urlpatterns = [
	path('profile/my-deals/', MyDealView.as_view(), name='my_deals')
]