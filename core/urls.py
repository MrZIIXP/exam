from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('contact/', views.ContactUsView.as_view(), name='contact'),
    path('about/', views.AboutUsView.as_view(), name='about'),
]