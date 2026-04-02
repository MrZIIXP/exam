from django.urls import path
from .views import FavouriteListView, AddFavouriteView, RemoveFavouriteView

urlpatterns = [
    path('favourites/', FavouriteListView.as_view(), name='favourites'),
    path('favourite/add/<int:pk>/', AddFavouriteView.as_view(), name='add_favourite'),
    path('favourite/remove/<int:pk>/', RemoveFavouriteView.as_view(), name='remove_favourite'),
]