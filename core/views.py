from django.views.generic import TemplateView
from catalog.models import Car, Brand, BodyStyle
from deals.models import Deal
from accounts.models import User


class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем featured cars (последние 4 добавленных автомобиля)
        context['featured_cars'] = Car.objects.filter(is_deleted=False).order_by('-created_at')[:4]
        
        # Получаем body styles для фильтрации
        context['body_styles'] = BodyStyle.objects.all()
        
        # Получаем бренды для поиска
        context['brands'] = Brand.objects.all()
        
        # Статистика для секции "Engineered for Trust"
        context['total_cars'] = Car.objects.filter(is_deleted=False).count()
        context['total_deals'] = Deal.objects.filter(status='delivered').count()
        context['total_users'] = User.objects.filter(is_verifired=True).count()
        
        return context


class ContactUsView(TemplateView):
    template_name = 'core/contact_us.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact Us'
        context['page_description'] = 'Get in touch with our concierge team'
        return context


class AboutUsView(TemplateView):
    template_name = 'core/about_us.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'About Us'
        context['page_description'] = 'Learn more about LUXE AUTO'
        return context