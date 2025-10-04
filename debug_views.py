from django.http import HttpResponse
from django.shortcuts import render
from shopping_cart.utils import get_or_create_cart
from shopping_cart.models import Cart, CartItem
import traceback

def debug_cart(request):
    """Debug view to test cart functionality on Heroku"""
    debug_info = []
    
    try:
        # Test 1: Basic cart data
        debug_info.append("=== CART DEBUG INFO ===")
        debug_info.append(f"User: {request.user}")
        debug_info.append(f"User authenticated: {request.user.is_authenticated}")
        debug_info.append(f"Session key: {getattr(request.session, 'session_key', 'NO SESSION KEY')}")
        
        # Test 2: Cart counts
        cart_count = Cart.objects.count()
        item_count = CartItem.objects.count()
        debug_info.append(f"Total carts: {cart_count}")
        debug_info.append(f"Total cart items: {item_count}")
        
        # Test 3: get_or_create_cart function
        debug_info.append("\n=== TESTING get_or_create_cart ===")
        cart = get_or_create_cart(request)
        debug_info.append(f"Cart created/retrieved: {cart}")
        debug_info.append(f"Cart items: {cart.items.count()}")
        
        # Test 4: Cart context
        debug_info.append("\n=== TESTING CART CONTEXT ===")
        cart_items = cart.items.select_related('product', 'size').all()
        debug_info.append(f"Cart items query: {len(cart_items)}")
        
        for item in cart_items:
            debug_info.append(f"  - {item.product.name} (qty: {item.quantity})")
        
        # Test 5: Template context variables
        debug_info.append("\n=== TESTING TEMPLATE CONTEXT ===")
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'cart_total_items': cart.total_items,
            'cart_subtotal': cart.subtotal,
            'cart_delivery_cost': cart.delivery_cost,
            'cart_total': cart.total,
        }
        
        for key, value in context.items():
            debug_info.append(f"{key}: {value}")
        
        debug_info.append("\n✓ ALL TESTS PASSED")
        
    except Exception as e:
        debug_info.append(f"\n✗ ERROR: {str(e)}")
        debug_info.append(f"Traceback:\n{traceback.format_exc()}")
    
    return HttpResponse("<pre>" + "\n".join(debug_info) + "</pre>")