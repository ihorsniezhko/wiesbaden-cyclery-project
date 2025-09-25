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
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key).first()
            if session_cart and session_cart != cart:
                merge_carts(session_cart, cart)
                session_cart.delete()
        
        return cart
    else:
        # For anonymous users, use session key
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart


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
    """
    cart = get_or_create_cart(request)
    
    # Check if item already exists in cart
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
    """
    cart = get_or_create_cart(request)
    
    try:
        cart_item = cart.items.get(product=product, size=size)
        if quantity <= 0:
            cart_item.delete()
            return None
        else:
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