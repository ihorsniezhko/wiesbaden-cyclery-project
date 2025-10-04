from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from products.models import Product, Size
from .utils import get_or_create_cart, add_to_cart, update_cart_item, remove_from_cart, clear_cart
import json


def cart_view(request):
    """
    Display the shopping cart with all items
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'size').all() if cart else []
    
    # Calculate free delivery delta
    free_delivery_threshold = 50.00  # €50 for free delivery
    free_delivery_delta = max(0, free_delivery_threshold - float(cart.subtotal)) if cart else free_delivery_threshold
    
    # Add stock information for each cart item
    cart_items_with_stock = []
    if cart_items:
        for item in cart_items:
            # Calculate available stock for this product
            other_cart_quantity = sum(
                cart_item.quantity for cart_item in cart_items 
                if cart_item.product == item.product and cart_item != item
            )
            max_available = item.product.stock_quantity - other_cart_quantity
            
            cart_items_with_stock.append({
                'item': item,
                'max_available': max_available,
                'stock_warning': item.quantity > item.product.stock_quantity,
                'exceeds_stock': item.quantity > max_available,
            })
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_items_with_stock': cart_items_with_stock,
        'cart_subtotal': cart.subtotal if cart else 0,
        'cart_delivery_cost': cart.delivery_cost if cart else 4.99,
        'cart_total': cart.total if cart else 0,
        'free_delivery_delta': free_delivery_delta,
    }
    
    # TODO: Full cart.html template causes 500 error on Heroku - needs investigation
    # Using simplified template for now until issue is resolved
    return render(request, 'shopping_cart/cart_simple.html', context)


@require_POST
def add_to_cart_view(request, product_id):
    """
    Add a product to the cart
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Get size if provided
    size_id = request.POST.get('size')
    size = None
    if size_id:
        try:
            size = Size.objects.get(id=size_id)
            # Verify size is valid for this product
            if not product.sizes.filter(id=size.id).exists():
                messages.error(request, f"Selected size is not available for {product.name}")
                return redirect('product_detail', product_id=product.id)
        except Size.DoesNotExist:
            messages.error(request, "Invalid size selected")
            return redirect('product_detail', product_id=product.id)
    
    # Check if product requires size but none provided
    if product.sizes.exists() and not size:
        messages.error(request, f"Please select a size for {product.name}")
        return redirect('product_detail', product_id=product.id)
    
    # Get quantity
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Add to cart
    try:
        cart_item = add_to_cart(request, product, size, quantity)
        size_info = f" ({size.display_name})" if size else ""
        messages.success(
            request, 
            f"Added {quantity}x {product.name}{size_info} to your cart"
        )
    except Exception as e:
        messages.error(request, f"Error adding item to cart: {str(e)}")
    
    # Redirect back to product or cart
    redirect_to = request.POST.get('redirect_to', 'shopping_cart:cart')
    if redirect_to == 'product_detail':
        return redirect('product_detail', product_id=product.id)
    else:
        return redirect('shopping_cart:cart')


@require_POST
def update_cart_view(request, product_id):
    """
    Update quantity of a cart item
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Get size if provided
    size_id = request.POST.get('size')
    size = None
    if size_id:
        try:
            size = Size.objects.get(id=size_id)
        except Size.DoesNotExist:
            messages.error(request, "Invalid size")
            return redirect('shopping_cart:cart')
    
    # Get new quantity
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 0:
            quantity = 0
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity")
        return redirect('shopping_cart:cart')
    
    # Update cart item
    try:
        if quantity == 0:
            # Remove item
            remove_from_cart(request, product, size)
            size_info = f" ({size.display_name})" if size else ""
            messages.success(request, f"Removed {product.name}{size_info} from your cart")
        else:
            # Update quantity
            cart_item = update_cart_item(request, product, size, quantity)
            if cart_item:
                size_info = f" ({size.display_name})" if size else ""
                messages.success(
                    request, 
                    f"Updated {product.name}{size_info} quantity to {quantity}"
                )
            else:
                messages.error(request, "Item not found in cart")
    except Exception as e:
        messages.error(request, f"Error updating cart: {str(e)}")
    
    return redirect('shopping_cart:cart')


@require_POST
def remove_from_cart_view(request, product_id):
    """
    Remove an item from the cart
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Get size if provided
    size_id = request.POST.get('size')
    size = None
    if size_id:
        try:
            size = Size.objects.get(id=size_id)
        except Size.DoesNotExist:
            messages.error(request, "Invalid size")
            return redirect('shopping_cart:cart')
    
    # Remove from cart
    try:
        success = remove_from_cart(request, product, size)
        if success:
            size_info = f" ({size.display_name})" if size else ""
            messages.success(request, f"Removed {product.name}{size_info} from your cart")
        else:
            messages.error(request, "Item not found in cart")
    except Exception as e:
        messages.error(request, f"Error removing item: {str(e)}")
    
    return redirect('shopping_cart:cart')


@require_POST
def clear_cart_view(request):
    """
    Clear all items from the cart
    """
    try:
        clear_cart(request)
        messages.success(request, "Cart cleared successfully")
    except Exception as e:
        messages.error(request, f"Error clearing cart: {str(e)}")
    
    return redirect('shopping_cart:cart')


# AJAX Views for dynamic cart updates

@require_POST
def ajax_add_to_cart(request, product_id):
    """
    AJAX view to add product to cart
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Parse JSON data
        data = json.loads(request.body)
        size_id = data.get('size')
        quantity = int(data.get('quantity', 1))
        
        size = None
        if size_id:
            size = get_object_or_404(Size, id=size_id)
            # Verify size is valid for this product
            if not product.sizes.filter(id=size.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Selected size is not available for this product'
                })
        
        # Check if product requires size but none provided
        if product.sizes.exists() and not size:
            return JsonResponse({
                'success': False,
                'error': 'Please select a size for this product'
            })
        
        # Add to cart
        cart_item = add_to_cart(request, product, size, quantity)
        cart = get_or_create_cart(request)
        
        size_info = f" ({size.display_name})" if size else ""
        
        return JsonResponse({
            'success': True,
            'message': f"Added {quantity}x {product.name}{size_info} to your cart",
            'cart_total_items': cart.total_items,
            'cart_total': float(cart.total),
            'cart_subtotal': float(cart.subtotal),
            'cart_delivery_cost': float(cart.delivery_cost)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
def ajax_update_cart(request, product_id):
    """
    AJAX view to update cart item quantity
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Parse JSON data
        data = json.loads(request.body)
        size_id = data.get('size')
        quantity = int(data.get('quantity', 1))
        
        size = None
        if size_id:
            size = get_object_or_404(Size, id=size_id)
        
        # Update cart item
        if quantity == 0:
            remove_from_cart(request, product, size)
            message = f"Removed {product.name} from your cart"
        else:
            cart_item = update_cart_item(request, product, size, quantity)
            if not cart_item:
                return JsonResponse({
                    'success': False,
                    'error': 'Item not found in cart'
                })
            message = f"Updated {product.name} quantity to {quantity}"
        
        cart = get_or_create_cart(request)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart.total_items,
            'cart_total': float(cart.total),
            'cart_subtotal': float(cart.subtotal),
            'cart_delivery_cost': float(cart.delivery_cost)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def cart_summary_ajax(request):
    """
    AJAX view to get cart summary
    """
    try:
        cart = get_or_create_cart(request)
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_total': float(cart.total),
            'cart_subtotal': float(cart.subtotal),
            'cart_delivery_cost': float(cart.delivery_cost)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })