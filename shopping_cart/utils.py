from django.contrib.sessions.models import Session
from .models import Cart, CartItem


def get_or_create_cart(request):
    """
    Get or create a cart for the current request
    Handles both authenticated users and anonymous sessions
    """
    if request.user.is_authenticated:
        # For authenticated users, get or create cart linked to user
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # If user was anonymous and now logged in, merge session cart
        try:
            session_key = getattr(request.session, 'session_key', None)
            if session_key:
                session_cart = Cart.objects.filter(session_key=session_key).first()
                if session_cart and session_cart != cart:
                    merge_carts(session_cart, cart)
                    session_cart.delete()
        except (AttributeError, TypeError):
            # Handle cases where session is not properly initialized
            pass
        
        return cart
    else:
        # For anonymous users, use session key
        try:
            if not getattr(request.session, 'session_key', None):
                request.session.create()
            
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            return cart
        except (AttributeError, TypeError):
            # Fallback: create a temporary cart without session
            # This should rarely happen in production
            return Cart.objects.create()


def merge_carts(source_cart, target_cart):
    """
    Merge items from source cart into target cart
    Used when anonymous user logs in
    """
    for source_item in source_cart.items.all():
        # Check if item already exists in target cart
        existing_item = target_cart.items.filter(
            product=source_item.product,
            size=source_item.size
        ).first()
        
        if existing_item:
            # Add quantities together
            existing_item.quantity += source_item.quantity
            existing_item.save()
        else:
            # Create new item in target cart
            CartItem.objects.create(
                cart=target_cart,
                product=source_item.product,
                size=source_item.size,
                quantity=source_item.quantity
            )


def add_to_cart(request, product, size=None, quantity=1):
    """
    Add a product to the cart with specified quantity and size
    Includes stock validation to prevent overselling
    """
    cart = get_or_create_cart(request)
    
    # Stock validation
    if not product.in_stock:
        raise ValueError(f"{product.name} is currently out of stock")
    
    # Check current quantity in cart for this product (all sizes combined for simplicity)
    current_cart_quantity = sum(
        item.quantity for item in cart.items.filter(product=product)
    )
    
    # Calculate total quantity after addition
    total_quantity = current_cart_quantity + quantity
    
    # Check if total quantity exceeds available stock
    if total_quantity > product.stock_quantity:
        available_to_add = product.stock_quantity - current_cart_quantity
        if available_to_add <= 0:
            raise ValueError(f"Cannot add more {product.name} - already have maximum available quantity in cart")
        else:
            raise ValueError(
                f"Only {available_to_add} more units of {product.name} can be added to cart "
                f"(you have {current_cart_quantity}, stock: {product.stock_quantity})"
            )
    
    # Check if item already exists in cart with same size
    existing_item = cart.items.filter(product=product, size=size).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        existing_item.save()
        return existing_item
    else:
        # Create new cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            size=size,
            quantity=quantity
        )
        return cart_item


def update_cart_item(request, product, size=None, quantity=1):
    """
    Update the quantity of a specific cart item
    Includes stock validation to prevent overselling
    """
    cart = get_or_create_cart(request)
    
    try:
        cart_item = cart.items.get(product=product, size=size)
        
        if quantity <= 0:
            cart_item.delete()
            return None
        else:
            # Stock validation for updates
            if not product.in_stock:
                raise ValueError(f"{product.name} is currently out of stock")
            
            # Check current quantity in cart for this product (excluding the item being updated)
            other_cart_quantity = sum(
                item.quantity for item in cart.items.filter(product=product).exclude(id=cart_item.id)
            )
            
            # Calculate total quantity after update
            total_quantity = other_cart_quantity + quantity
            
            # Check if total quantity exceeds available stock
            if total_quantity > product.stock_quantity:
                max_allowed = product.stock_quantity - other_cart_quantity
                raise ValueError(
                    f"Cannot set quantity to {quantity}. Maximum allowed: {max_allowed} "
                    f"(stock: {product.stock_quantity}, other items in cart: {other_cart_quantity})"
                )
            
            cart_item.quantity = quantity
            cart_item.save()
            return cart_item
            
    except CartItem.DoesNotExist:
        return None


def remove_from_cart(request, product, size=None):
    """
    Remove a specific item from the cart
    """
    cart = get_or_create_cart(request)
    
    try:
        cart_item = cart.items.get(product=product, size=size)
        cart_item.delete()
        return True
    except CartItem.DoesNotExist:
        return False


def clear_cart(request):
    """
    Remove all items from the cart
    """
    cart = get_or_create_cart(request)
    cart.clear()
    return True


def get_available_stock(request, product):
    """
    Get the available stock for a product considering items already in user's cart
    """
    if not product.in_stock:
        return 0
    
    cart = get_or_create_cart(request)
    current_cart_quantity = sum(
        item.quantity for item in cart.items.filter(product=product)
    )
    
    available = product.stock_quantity - current_cart_quantity
    return max(0, available)


def get_cart_quantity_for_product(request, product):
    """
    Get the total quantity of a product currently in the user's cart
    """
    cart = get_or_create_cart(request)
    return sum(item.quantity for item in cart.items.filter(product=product))