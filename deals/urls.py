from django.urls import path
from .views import MyDealsView, CreateDealView, UpdateDealStatusView, DeleteDealView

urlpatterns = [
    path('profile/my-deals/', MyDealsView.as_view(), name='my_deals'),
    path('deal/create/<int:pk>/', CreateDealView.as_view(), name='create_deal'),
    path('deal/update/<int:pk>/', UpdateDealStatusView.as_view(), name='update_deal'),
    path('deal/delete/<int:pk>/', DeleteDealView.as_view(), name='delete_deal'),
]