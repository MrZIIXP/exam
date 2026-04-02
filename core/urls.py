from django.urls import path
from .views import HomeView, ContactUsView, AboutUsView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path('about/', AboutUsView.as_view(), name='about'),
]