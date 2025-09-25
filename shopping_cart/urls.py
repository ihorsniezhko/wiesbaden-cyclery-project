from django.urls import path
from . import views

app_name = 'shopping_cart'

urlpatterns = [
    # Main cart view
    path('', views.cart_view, name='cart'),
    
    # Cart management views
    path('add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('update/<int:product_id>/', views.update_cart_view, name='update_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('clear/', views.clear_cart_view, name='clear_cart'),
    
    # AJAX views
    path('ajax/add/<int:product_id>/', views.ajax_add_to_cart, name='ajax_add_to_cart'),
    path('ajax/update/<int:product_id>/', views.ajax_update_cart, name='ajax_update_cart'),
    path('ajax/summary/', views.cart_summary_ajax, name='ajax_cart_summary'),
]