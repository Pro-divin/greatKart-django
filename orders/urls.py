from django.urls import path
from . import views
from .views import payment_failed

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'), 
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('flutterwave/callback/', views.flutterwave_callback, name='flutterwave_callback'),
    path('payment_failed/', payment_failed, name='payment_failed'),
    

   
    
    

] 
