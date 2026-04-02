from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect
from .models import Car, BodyStyle, Brand, Transmission
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import Http404
from favourites.models import Favourite     

class CatalogView(ListView):
    template_name = 'core/catalog.html'
    model = Car
    context_object_name = 'cars'

    def get_queryset(self):
        queryset = Car.objects.filter(is_deleted=False)
        
        brand_id = self.request.GET.get('brand')
        if brand_id:
            queryset = queryset.filter(brand__id=brand_id)
        
        body_style_id = self.request.GET.get('body_style')
        if body_style_id:
            queryset = queryset.filter(body_style__id=body_style_id)
        
        transmission_id = self.request.GET.get('transmission')
        if transmission_id:
            queryset = queryset.filter(transmission__id=transmission_id)
        
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=int(max_price))
            except ValueError:
                pass
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        sort_by = self.request.GET.get('sort')
        if sort_by:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['body_styles'] = BodyStyle.objects.all()
        context['transmissions'] = Transmission.objects.all()
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_body_style'] = self.request.GET.get('body_style', '')
        context['selected_transmission'] = self.request.GET.get('transmission', '')
        context['selected_max_price'] = self.request.GET.get('max_price', '')
        context['selected_sort'] = self.request.GET.get('sort', '-created_at')
        context['search_query'] = self.request.GET.get('search', '')
        context['total_results'] = self.get_queryset().count()
        
        user_id = self.request.session.get('user_id')
        if user_id:
            favourite_car_ids = Favourite.objects.filter(user_id=user_id).values_list('car_id', flat=True)
            context['favourite_car_ids'] = list(favourite_car_ids)
        else:
            context['favourite_car_ids'] = []
        
        return context

class CatalogDetail(DetailView):
    template_name = 'core/car_details.html'
    context_object_name = 'car'
    model = Car

    def get_queryset(self):
        return Car.objects.filter(is_deleted=False)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("This listing has been deleted")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()

        from review.models import Review
        from django.db.models import Avg

        reviews = Review.objects.filter(to_user=car.user)
        rating_data = reviews.aggregate(avg_rating=Avg('rating'))

        context['user_rating'] = round(rating_data['avg_rating'] or 0, 1)
        context['reviews_count'] = reviews.count()

        context['similar_cars'] = Car.objects.filter(
            is_deleted=False,
            brand=car.brand
        ).exclude(id=car.id)[:3]

        return context


class SendMessageView(View):
    def post(self, request, pk):
        car = get_object_or_404(Car, id=pk, is_deleted=False)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            try:
                send_mail(
                    f"New inquiry about {car.title}",
                    f"From: {name}\nEmail: {email}\n\nMessage:\n{message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [car.user.email],
                    fail_silently=False,
                )
                messages.success(
                    request, 'Message sent successfully! The seller will contact you soon.')
            except Exception as e:
                messages.error(request, f'Error sending message: {e}')
        else:
            messages.error(request, 'Please fill in all fields')

        return redirect('car_detail', pk=pk)
