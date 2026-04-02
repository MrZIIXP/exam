from django.shortcuts import render
from django.views.generic import TemplateView

class MyDealView(TemplateView):
   template_name = 'profile/my_deals.html'