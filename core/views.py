from django.views.generic import TemplateView, View
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from catalog.models import Car, Brand, BodyStyle
from deals.models import Deal
from accounts.models import User


class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_cars'] = Car.objects.filter(is_deleted=False).order_by('-created_at')[:4]
        context['body_styles'] = BodyStyle.objects.all()
        context['brands'] = Brand.objects.all()
        context['total_cars'] = Car.objects.filter(is_deleted=False).count()
        context['total_deals'] = Deal.objects.filter(status='delivered').count()
        context['total_users'] = User.objects.filter(is_verifired=True).count()
        return context


class ContactUsView(View):
    template_name = 'core/contact_us.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        model = request.POST.get('model')
        inquiry_type = request.POST.get('inquiry_type')
        message = request.POST.get('message')
        
        if not all([name, email, message]):
            messages.error(request, 'Please fill in all required fields')
            return render(request, self.template_name)
        
        try:
            admin_subject = f"New Contact Form Inquiry from {name}"
            admin_message = f"""
            Name: {name}
            Email: {email}
            Interested Model: {model or 'Not specified'}
            Inquiry Type: {inquiry_type or 'General'}
            
            Message:
            {message}
            """
            
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            user_subject = "Thank you for contacting LUXE AUTO"
            user_message = f"""
            Dear {name},
            
            Thank you for reaching out to LUXE AUTO Concierge Team.
            
            We have received your inquiry regarding {model or 'our vehicles'} and will get back to you within 24 hours.
            
            Your message:
            "{message}"
            
            Best regards,
            LUXE AUTO Concierge Team
            """
            
            send_mail(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent successfully! Our concierge will contact you soon.')
            return redirect('contact')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}. Please try again later.')
            return render(request, self.template_name)


class AboutUsView(TemplateView):
    template_name = 'core/about_us.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'About Us'
        context['page_description'] = 'Learn more about LUXE AUTO'
        return context