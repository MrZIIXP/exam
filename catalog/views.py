from django.views.generic import ListView
from .models import Car, BodyStyle, Brand, Transmission
from django.db.models import Q


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
        
        return context