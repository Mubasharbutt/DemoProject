from django.urls import path
from .views import  AddItemView,OrderListAPI,OrderDetailAPI,AllItemsView,PaymentView

urlpatterns = [
    
    path('add-item/', AddItemView.as_view(), name='add_item'),
    path('orders/', OrderListAPI.as_view(), name='order-list'),
    path('orders/<int:id>/', OrderDetailAPI.as_view(), name='order-detail'),
    path('cart/', AllItemsView.as_view(), name='cart'),
    #this extra endpoint for payments
    path('payment/<int:order_id>/', PaymentView.as_view(), name='payment'),

    



]
