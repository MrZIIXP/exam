from django.urls import path
from .views import *
urlpatterns = [
    path('profile/<int:pk>/add-review/',
         AddReviewView.as_view(), name='add_review'),
    path('profile/review/delete/<int:pk>/',
         DeleteReviewView.as_view(), name='delete_review'),

]
