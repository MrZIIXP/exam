from django.views.generic import ListView, View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Favourite
from catalog.models import Car
from accounts.models import User


class FavouriteListView(ListView):
    template_name = 'profile/my_favourites.html'
    context_object_name = 'favourites'
    
    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            return Favourite.objects.filter(user_id=user_id).select_related('car', 'car__brand', 'car__transmission', 'car__body_style')
        return Favourite.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_favourites'] = self.get_queryset().count()
        return context


class AddFavouriteView(View):
    def get(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login to add favourites')
            return redirect('login')
        
        car = get_object_or_404(Car, id=pk, is_deleted=False)
        user = get_object_or_404(User, id=user_id)
        
        favourite, created = Favourite.objects.get_or_create(
            user=user,
            car=car
        )
        
        if created:
            messages.success(request, f'Added "{car.title}" to favourites')
        else:
            messages.info(request, f'"{car.title}" is already in favourites')
        
        return redirect(request.META.get('HTTP_REFERER', 'catalog'))


class RemoveFavouriteView(View):
    def get(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login to remove favourites')
            return redirect('login')
        
        car = get_object_or_404(Car, id=pk)
        
        Favourite.objects.filter(user_id=user_id, car=car).delete()
        messages.success(request, f'Removed "{car.title}" from favourites')
        
        return redirect(request.META.get('HTTP_REFERER', 'favourites'))