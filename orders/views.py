from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.conf import settings
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
from .emails import send_order_confirmation_email


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
        
        # Get client secret from POST data
        client_secret = request.POST.get('client_secret', '').strip()
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"DEBUG: POST data keys: {list(request.POST.keys())}")
        logger.error(f"DEBUG: client_secret present: {bool(client_secret)}")
        logger.error(f"DEBUG: client_secret value: {client_secret[:20] if client_secret else 'NONE'}...")
        
        # Verify Stripe payment was successful
        if not client_secret:
            messages.error(request, 'Payment information is missing. Please try again.')
            logger.error("DEBUG: Redirecting due to missing client_secret")
            return redirect('orders:checkout')
        
        # Verify payment intent with Stripe
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            logger.error("DEBUG: About to verify payment with Stripe")
            
            # Extract payment intent ID from client secret
            payment_intent_id = client_secret.split('_secret')[0]
            logger.error(f"DEBUG: Payment Intent ID: {payment_intent_id}")
            
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            logger.error(f"DEBUG: Payment Intent retrieved, status: {payment_intent.status}")
            
            # Check if payment was successful
            if payment_intent.status != 'succeeded':
                logger.error(f"DEBUG: Payment not succeeded, status: {payment_intent.status}")
                messages.error(
                    request, 
                    f'Payment was not completed. Status: {payment_intent.status}. Please try again.'
                )
                return redirect('orders:checkout')
            
            logger.error("DEBUG: Payment verification passed!")
                
        except Exception as e:
            logger.error(f"DEBUG: Payment verification exception: {str(e)}")
            messages.error(request, f'Payment verification failed: {str(e)}')
            return redirect('orders:checkout')
        
        # Validate order data
        logger.error("DEBUG: About to validate order data")
        validation_errors = validate_order_data(form, cart)
        if validation_errors:
            logger.error(f"DEBUG: Validation errors found: {validation_errors}")
            for error in validation_errors:
                messages.error(request, error)
        else:
            logger.error("DEBUG: Validation passed, creating order")
            try:
                # Create order from cart
                order = create_order_from_cart(request, form)
                logger.error(f"DEBUG: Order created: {order.order_number}")
                
                # Update product stock
                update_product_stock(order)
                
                # Send order confirmation email
                email_sent = send_order_confirmation_email(order)
                
                # Clear the cart
                clear_cart(request)
                
                # Success message
                if email_sent:
                    messages.success(
                        request, 
                        f'Order {order.order_number} has been created successfully! '
                        f'A confirmation email has been sent to {order.email}.'
                    )
                else:
                    messages.success(
                        request, 
                        f'Order {order.order_number} has been created successfully!'
                    )
                    messages.warning(
                        request,
                        'Note: Confirmation email could not be sent. Please check your email settings.'
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
                    'full_name': profile.get_full_name() or f"{request.user.first_name} {request.user.last_name}".strip(),
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
    
    # Create Stripe payment intent for the checkout
    stripe_total = round(cart.total * 100)  # Stripe expects amount in cents
    client_secret = None
    
    try:
        from .stripe_utils import create_payment_intent
        payment_intent = create_payment_intent(
            amount=cart.total,
            currency=settings.STRIPE_CURRENCY,
            metadata={
                'cart_id': str(cart.id),
                'user_id': str(request.user.id) if request.user.is_authenticated else 'anonymous',
            }
        )
        if payment_intent:
            client_secret = payment_intent.client_secret
    except Exception as e:
        messages.error(request, f'Payment system error: {str(e)}')
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.items.select_related('product', 'size').all(),
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_currency': settings.STRIPE_CURRENCY,
        'client_secret': client_secret,
        'product_count': cart.total_items,
        'total': cart.subtotal,
        'delivery': cart.delivery_cost,
        'grand_total': cart.total,
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
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.conf import settings
from .stripe_utils import create_payment_intent, get_stripe_error_message
from .payment_errors import handle_payment_error, get_error_recovery_instructions
import json
import stripe
import logging

logger = logging.getLogger(__name__)

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

@require_POST
def create_payment_intent_view(request):
    """
    AJAX view to create Stripe payment intent
    """
    try:
        cart = get_or_create_cart(request)
        
        if not cart or cart.total_items == 0:
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Get order form data for metadata
        try:
            form_data = json.loads(request.body)
        except json.JSONDecodeError:
            form_data = {}
        
        # Create metadata for the payment intent
        metadata = {
            'cart_id': str(cart.id),
            'user_id': str(request.user.id) if request.user.is_authenticated else 'anonymous',
            'customer_email': form_data.get('email', ''),
            'customer_name': form_data.get('full_name', ''),
            'order_total': str(cart.total),
            'delivery_cost': str(cart.delivery_cost),
            'items_count': str(cart.total_items),
        }
        
        # Create payment intent with comprehensive error handling
        try:
            payment_intent = create_payment_intent(
                amount=cart.total,
                currency=settings.STRIPE_CURRENCY,
                metadata=metadata
            )
            
            if payment_intent:
                return JsonResponse({
                    'success': True,
                    'client_secret': payment_intent.client_secret,
                    'payment_intent_id': payment_intent.id,
                    'amount': int(cart.total * 100),  # Amount in cents
                    'currency': settings.STRIPE_CURRENCY,
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to create payment intent. Please try again.',
                    'error_code': 'payment_intent_creation_failed',
                    'retry_allowed': True
                }, status=500)
                
        except stripe.error.StripeError as e:
            # Handle Stripe-specific errors
            error_response = handle_payment_error(e, context='payment_intent_creation')
            return JsonResponse(error_response, status=400)
            
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in payment intent creation: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.',
            'error_code': 'unexpected_error',
            'retry_allowed': True
        }, status=500)


@require_POST
def process_payment_view(request):
    """
    Process payment after successful Stripe confirmation
    """
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        
        if not payment_intent_id:
            return JsonResponse({'error': 'Payment intent ID is required'}, status=400)
        
        # Get cart
        cart = get_or_create_cart(request)
        if not cart or cart.total_items == 0:
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Get order form data
        order_form_data = data.get('order_form', {})
        form = OrderForm(order_form_data)
        
        # Validate order data
        validation_errors = validate_order_data(form, cart)
        if validation_errors:
            return JsonResponse({
                'error': 'Order validation failed',
                'validation_errors': validation_errors
            }, status=400)
        
        # Create order with comprehensive error handling
        try:
            order = create_order_from_cart(request, form)
            order.payment_intent_id = payment_intent_id
            order.payment_status = 'processing'
            order.save()
            
            # Update product stock with error handling
            try:
                update_product_stock(order)
            except ValueError as stock_error:
                # Stock error - cancel the order
                order.status = 'cancelled'
                order.payment_status = 'failed'
                order.order_notes = f"Order cancelled due to stock error: {str(stock_error)}"
                order.save()
                
                return JsonResponse({
                    'success': False,
                    'error': 'Some items are no longer in stock. Your payment will be refunded.',
                    'error_code': 'insufficient_stock',
                    'retry_allowed': False
                }, status=400)
            
            # Clear the cart
            clear_cart(request)
            
            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'redirect_url': f'/orders/confirmation/{order.order_number}/'
            })
            
        except Exception as order_error:
            logger.error(f"Order creation error: {str(order_error)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Failed to create order. Please contact support.',
                'error_code': 'order_creation_failed',
                'retry_allowed': False
            }, status=500)
        
    except Exception as e:
        logger.error(f"Unexpected error in payment processing: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please contact support.',
            'error_code': 'unexpected_error',
            'retry_allowed': False
        }, status=500)
@require_POST
def payment_error_recovery(request):
    """
    Handle payment error recovery and provide guidance
    """
    try:
        data = json.loads(request.body)
        error_code = data.get('error_code')
        payment_intent_id = data.get('payment_intent_id')
        
        if not error_code:
            return JsonResponse({
                'success': False,
                'error': 'Error code is required'
            }, status=400)
        
        # Get recovery instructions
        recovery_info = get_error_recovery_instructions(error_code)
        
        # If we have a payment intent ID, try to get more details
        additional_info = {}
        if payment_intent_id:
            try:
                from .stripe_utils import retrieve_payment_intent
                payment_intent = retrieve_payment_intent(payment_intent_id)
                
                if payment_intent:
                    additional_info = {
                        'payment_status': payment_intent.status,
                        'last_payment_error': payment_intent.last_payment_error,
                        'amount': payment_intent.amount / 100,
                        'currency': payment_intent.currency
                    }
            except Exception as e:
                logger.warning(f"Could not retrieve payment intent details: {e}")
        
        return JsonResponse({
            'success': True,
            'recovery_info': recovery_info,
            'additional_info': additional_info,
            'support_contact': {
                'email': getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
                'phone': getattr(settings, 'SUPPORT_PHONE', None)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in payment recovery: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Could not retrieve recovery information'
        }, status=500)


def payment_error_page(request):
    """
    Display payment error page with recovery options
    """
    error_code = request.GET.get('error_code', 'unknown')
    payment_intent_id = request.GET.get('payment_intent_id')
    order_number = request.GET.get('order_number')
    
    # Get recovery information
    recovery_info = get_error_recovery_instructions(error_code)
    
    # Get order if available
    order = None
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            pass
    
    context = {
        'error_code': error_code,
        'recovery_info': recovery_info,
        'payment_intent_id': payment_intent_id,
        'order': order,
        'support_email': getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
        'support_phone': getattr(settings, 'SUPPORT_PHONE', None),
    }
    
    return render(request, 'orders/payment_error.html', context)


@require_POST
def retry_payment_intent(request):
    """
    Create a new payment intent for retry attempts
    """
    try:
        data = json.loads(request.body)
        original_payment_intent_id = data.get('original_payment_intent_id')
        
        if not original_payment_intent_id:
            return JsonResponse({
                'success': False,
                'error': 'Original payment intent ID is required'
            }, status=400)
        
        # Find the order associated with the failed payment
        try:
            order = Order.objects.get(payment_intent_id=original_payment_intent_id)
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Order not found for retry'
            }, status=404)
        
        # Create new payment intent for retry
        metadata = {
            'order_number': order.order_number,
            'retry_attempt': 'true',
            'original_payment_intent': original_payment_intent_id,
            'customer_email': order.email,
            'customer_name': order.full_name,
        }
        
        try:
            payment_intent = create_payment_intent(
                amount=order.grand_total,
                currency=settings.STRIPE_CURRENCY,
                metadata=metadata
            )
            
            if payment_intent:
                # Update order with new payment intent
                order.payment_intent_id = payment_intent.id
                order.payment_status = 'pending'
                order.save()
                
                # Create status history entry
                OrderStatusHistory.objects.create(
                    order=order,
                    status=order.status,
                    notes=f"Payment retry initiated. New payment intent: {payment_intent.id}"
                )
                
                return JsonResponse({
                    'success': True,
                    'client_secret': payment_intent.client_secret,
                    'payment_intent_id': payment_intent.id,
                    'order_number': order.order_number
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to create retry payment intent'
                }, status=500)
                
        except stripe.error.StripeError as e:
            error_response = handle_payment_error(e, order, 'payment_retry')
            return JsonResponse(error_response, status=400)
        
    except Exception as e:
        logger.error(f"Error in payment retry: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Could not process payment retry'
        }, status=500)