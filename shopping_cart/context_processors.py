from django.conf import settings
from .models import Cart


def cart_contents(request):
    """
    Context processor to make cart contents available in all templates
    """
    cart = None
    cart_items = []
    total_items = 0
    subtotal = 0
    delivery_cost = 0
    total = 0
    free_delivery_threshold = getattr(settings, 'FREE_DELIVERY_THRESHOLD', 50.00)
    free_delivery_delta = free_delivery_threshold  # Default to full amount needed

    try:
        if request.user.is_authenticated:
            # Get or create cart for authenticated user
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # Get cart for anonymous user using session
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()

        if cart:
            cart_items = cart.items.select_related('product', 'size').all()
            total_items = cart.total_items
            subtotal = cart.subtotal
            delivery_cost = cart.delivery_cost
            total = cart.total
            
            # Calculate free delivery delta using settings threshold
            free_delivery_delta = max(0, free_delivery_threshold - float(subtotal))

    except Exception:
        # Fallback to empty cart if any errors occur
        pass

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total_items': total_items,
        'cart_subtotal': subtotal,
        'cart_delivery_cost': delivery_cost,
        'cart_total': total,
        'free_delivery_delta': free_delivery_delta,
    }

    return context