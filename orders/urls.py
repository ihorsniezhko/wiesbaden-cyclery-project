from django.urls import path
from . import views
from .webhooks import stripe_webhook

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
    path('ajax/create-payment-intent/', views.create_payment_intent_view, name='ajax_create_payment_intent'),
    path('ajax/process-payment/', views.process_payment_view, name='ajax_process_payment'),
    path('ajax/payment-error-recovery/', views.payment_error_recovery, name='ajax_payment_error_recovery'),
    path('ajax/retry-payment/', views.retry_payment_intent, name='ajax_retry_payment'),
    
    # Error pages
    path('payment-error/', views.payment_error_page, name='payment_error'),
    
    # Stripe webhook
    path('webhook/', stripe_webhook, name='stripe_webhook'),  # Main webhook endpoint
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook_alt'),
    path('wh/', stripe_webhook, name='stripe_webhook_short'),  # For Stripe CLI
]