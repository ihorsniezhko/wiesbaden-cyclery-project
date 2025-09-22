from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from shopping_cart.utils import get_or_create_cart, clear_cart
from .models import Order, OrderLineItem
from .forms import OrderForm, OrderSearchForm
from .utils import (
    create_order_from_cart, 
    validate_order_data, 
    update_product_stock,
    get_user_orders,
    get_order_summary
)


def checkout(request):
    """
    Handle the checkout process
    """
    cart = get_or_create_cart(request)
    
    # Check if cart is empty
    if not cart or cart.total_items == 0:
        messages.error(request, "Your cart is empty. Add some items before checkout.")
        return redirect('shopping_cart:cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        # Validate order data
        validation_errors = validate_order_data(form, cart)
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
        else:
            try:
                # Create order from cart
                order = create_order_from_cart(request, form)
                
                # Update product stock
                update_product_stock(order)
                
                # Clear the cart
                clear_cart(request)
                
                # Success message
                messages.success(
                    request, 
                    f'Order {order.order_number} has been created successfully! '
                    f'A confirmation email will be sent to {order.email}.'
                )
                
                # Redirect to order confirmation
                return redirect('orders:order_confirmation', order_number=order.order_number)
                
            except Exception as e:
                messages.error(request, f'There was an error processing your order: {str(e)}')
    else:
        # Pre-populate form with user profile data if available
        initial_data = {}
        if request.user.is_authenticated:
            try:
                from accounts.models import UserProfile
                profile = UserProfile.objects.get(user=request.user)
                initial_data = {
                    'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                    'email': request.user.email,
                    'phone_number': profile.default_phone_number,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'town_or_city': profile.default_town_or_city,
                    'county': profile.default_county,
                    'postcode': profile.default_postcode,
                    'country': profile.default_country,
                }
            except:
                pass
        
        form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.items.select_related('product', 'size').all(),
    }
    
    return render(request, 'orders/checkout.html', context)


def order_confirmation(request, order_number):
    """
    Display order confirmation page
    """
    order = get_object_or_404(Order, order_number=order_number)
    
    # Check if user has permission to view this order
    if request.user.is_authenticated:
        # Authenticated users can only view their own orders
        if order.user_profile and order.user_profile.user != request.user:
            return HttpResponseForbidden("You don't have permission to view this order.")
    else:
        # For anonymous users, we'll allow viewing for a short time after creation
        # In a real application, you might want to use a secure token system
        pass
    
    order_summary = get_order_summary(order)
    
    context = {
        'order': order,
        'order_summary': order_summary,
    }
    
    return render(request, 'orders/order_confirmation.html', context)


@login_required
def order_history(request):
    """
    Display user's order history
    """
    orders = get_user_orders(request.user)
    
    # Search functionality
    search_form = OrderSearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        status = search_form.cleaned_data.get('status')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search_query:
            orders = orders.filter(
                Q(order_number__icontains=search_query) |
                Q(full_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        if status:
            orders = orders.filter(status=status)
        
        if date_from:
            orders = orders.filter(date__date__gte=date_from)
        
        if date_to:
            orders = orders.filter(date__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'orders': page_obj.object_list,
    }
    
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_number):
    """
    Display detailed view of a specific order
    """
    order = get_object_or_404(Order, order_number=order_number)
    
    # Check if user has permission to view this order
    if order.user_profile and order.user_profile.user != request.user:
        return HttpResponseForbidden("You don't have permission to view this order.")
    
    order_summary = get_order_summary(order)
    
    context = {
        'order': order,
        'order_summary': order_summary,
    }
    
    return render(request, 'orders/order_detail.html', context)


def order_tracking(request):
    """
    Allow users to track orders by order number
    """
    order = None
    error_message = None
    
    if request.method == 'POST':
        order_number = request.POST.get('order_number', '').strip().upper()
        email = request.POST.get('email', '').strip().lower()
        
        if order_number and email:
            try:
                order = Order.objects.get(order_number=order_number, email=email)
            except Order.DoesNotExist:
                error_message = "Order not found. Please check your order number and email address."
        else:
            error_message = "Please provide both order number and email address."
    
    context = {
        'order': order,
        'error_message': error_message,
    }
    
    return render(request, 'orders/order_tracking.html', context)


# AJAX Views for dynamic updates

from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def order_status_ajax(request, order_number):
    """
    AJAX view to get order status
    """
    try:
        order = Order.objects.get(order_number=order_number)
        
        # Check permissions
        if request.user.is_authenticated:
            if order.user_profile and order.user_profile.user != request.user:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'date': order.date.isoformat(),
            'total': float(order.grand_total),
        })
        
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def checkout_summary_ajax(request):
    """
    AJAX view to get checkout summary
    """
    try:
        cart = get_or_create_cart(request)
        
        if not cart or cart.total_items == 0:
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': float(cart.subtotal),
            'cart_delivery_cost': float(cart.delivery_cost),
            'cart_total': float(cart.total),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)