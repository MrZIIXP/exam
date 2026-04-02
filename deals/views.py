from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Deal
from catalog.models import Car
from accounts.models import User


class MyDealsView(ListView):
    template_name = 'profile/my_deals.html'
    context_object_name = 'deals'
    
    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            return Deal.objects.filter(buyer_id=user_id).select_related('car', 'seller', 'car__brand')
        return Deal.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('user_id')
        if user_id:
            context['selling_deals'] = Deal.objects.filter(seller_id=user_id).select_related('car', 'buyer', 'car__brand')
        else:
            context['selling_deals'] = []
        return context


class CreateDealView(View):
    def post(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login to purchase')
            return redirect('login')
        
        car = get_object_or_404(Car, id=pk, is_deleted=False)
        
        if car.user.id == user_id:
            messages.error(request, 'You cannot buy your own car')
            return redirect('car_detail', pk=pk)
        
        existing_deal = Deal.objects.filter(car=car, status__in=['processing', 'in_transit']).first()
        if existing_deal:
            messages.error(request, 'This car is already in a deal')
            return redirect('car_detail', pk=pk)
        
        deal = Deal.objects.create(
            seller=car.user,
            buyer_id=user_id,
            car=car,
            status='processing'
        )
        
        messages.success(request, f'Deal created for {car.title}! The seller will contact you soon.')
        return redirect('my_deals')


class UpdateDealStatusView(View):
    """Обновление статуса сделки без шаблона"""
    def post(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login')
            return redirect('login')
        
        deal = get_object_or_404(Deal, id=pk)
        
        # Проверяем, что пользователь является продавцом
        if deal.seller.id != user_id:
            messages.error(request, 'You are not the seller of this deal')
            return redirect('my_deals')
        
        new_status = request.POST.get('status')
        if new_status in ['processing', 'in_transit', 'delivered', 'cancelled']:
            deal.status = new_status
            deal.save()
            messages.success(request, f'Deal status updated to {deal.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
        
        return redirect('my_deals')


class DeleteDealView(View):
    def get(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Please login')
            return redirect('login')
        
        deal = get_object_or_404(Deal, id=pk)
        
        # Проверяем, что пользователь является участником сделки
        if deal.seller.id != user_id and deal.buyer.id != user_id:
            messages.error(request, 'You are not part of this deal')
            return redirect('my_deals')
        
        title = deal.car.title
        deal.delete()
        messages.success(request, f'Deal for {title} cancelled successfully')
        
        return redirect('my_deals')