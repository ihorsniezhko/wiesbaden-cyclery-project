from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout workflow
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    
    # Order management
    path('history/', views.order_history, name='order_history'),
    path('detail/<str:order_number>/', views.order_detail, name='order_detail'),
    path('tracking/', views.order_tracking, name='order_tracking'),
    
    # AJAX views
    path('ajax/status/<str:order_number>/', views.order_status_ajax, name='ajax_order_status'),
    path('ajax/checkout-summary/', views.checkout_summary_ajax, name='ajax_checkout_summary'),
]