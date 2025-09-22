import json
from decimal import Decimal
from django.conf import settings
from .models import Order, OrderLineItem
from shopping_cart.utils import get_or_create_cart


def create_order_from_cart(request, order_form):
    """
    Create an order from the current cart contents
    """
    cart = get_or_create_cart(request)
    
    if not cart or cart.total_items == 0:
        raise ValueError("Cannot create order from empty cart")
    
    # Create the order
    order = Order(
        full_name=order_form.cleaned_data['full_name'],
        email=order_form.cleaned_data['email'],
        phone_number=order_form.cleaned_data['phone_number'],
        street_address1=order_form.cleaned_data['street_address1'],
        street_address2=order_form.cleaned_data['street_address2'],
        town_or_city=order_form.cleaned_data['town_or_city'],
        county=order_form.cleaned_data['county'],
        postcode=order_form.cleaned_data['postcode'],
        country=order_form.cleaned_data['country'],
        original_cart=json.dumps({
            'cart_id': cart.id,
            'items': [
                {
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'size_id': item.size.id if item.size else None,
                    'size_name': item.size.display_name if item.size else None,
                    'quantity': item.quantity,
                    'price': str(item.product.price)
                }
                for item in cart.items.all()
            ]
        })
    )
    
    # Link to user profile if user is authenticated
    if request.user.is_authenticated:
        try:
            from accounts.models import UserProfile
            user_profile = UserProfile.objects.get(user=request.user)
            order.user_profile = user_profile
        except UserProfile.DoesNotExist:
            pass
    
    order.save()
    
    # Create order line items from cart items
    for cart_item in cart.items.all():
        order_line_item = OrderLineItem(
            order=order,
            product=cart_item.product,
            size=cart_item.size,
            quantity=cart_item.quantity,
        )
        order_line_item.save()
    
    return order


def calculate_order_totals(order):
    """
    Calculate and update order totals
    """
    order.update_total()
    return order


def get_order_summary(order):
    """
    Get a summary of the order for display
    """
    return {
        'order_number': order.order_number,
        'date': order.date,
        'status': order.status,
        'full_name': order.full_name,
        'email': order.email,
        'delivery_address': {
            'street_address1': order.street_address1,
            'street_address2': order.street_address2,
            'town_or_city': order.town_or_city,
            'county': order.county,
            'postcode': order.postcode,
            'country': order.country,
        },
        'items': [
            {
                'product': item.product,
                'size': item.size,
                'quantity': item.quantity,
                'lineitem_total': item.lineitem_total,
            }
            for item in order.lineitems.all()
        ],
        'order_total': order.order_total,
        'delivery_cost': order.delivery_cost,
        'grand_total': order.grand_total,
        'total_items': order.total_items,
    }


def validate_order_data(order_form, cart):
    """
    Validate order data before creation
    """
    errors = []
    
    # Check if cart is not empty
    if not cart or cart.total_items == 0:
        errors.append("Cannot checkout with an empty cart")
    
    # Check if all cart items are still in stock
    if cart:
        for cart_item in cart.items.all():
            if not cart_item.product.in_stock:
                errors.append(f"{cart_item.product.name} is no longer in stock")
            elif cart_item.product.stock_quantity < cart_item.quantity:
                errors.append(
                    f"Only {cart_item.product.stock_quantity} units of "
                    f"{cart_item.product.name} are available"
                )
    
    # Validate form data
    if not order_form.is_valid():
        for field, field_errors in order_form.errors.items():
            for error in field_errors:
                errors.append(f"{field}: {error}")
    
    return errors


def update_product_stock(order):
    """
    Update product stock quantities after order creation
    """
    for line_item in order.lineitems.all():
        product = line_item.product
        if product.stock_quantity >= line_item.quantity:
            product.stock_quantity -= line_item.quantity
            product.save()
        else:
            # This shouldn't happen if validation is working correctly
            raise ValueError(
                f"Insufficient stock for {product.name}. "
                f"Available: {product.stock_quantity}, Required: {line_item.quantity}"
            )


def restore_product_stock(order):
    """
    Restore product stock quantities if order is cancelled
    """
    for line_item in order.lineitems.all():
        product = line_item.product
        product.stock_quantity += line_item.quantity
        product.save()


def get_user_orders(user):
    """
    Get all orders for a specific user
    """
    try:
        from accounts.models import UserProfile
        user_profile = UserProfile.objects.get(user=user)
        return Order.objects.filter(user_profile=user_profile).order_by('-date')
    except UserProfile.DoesNotExist:
        return Order.objects.none()


def format_order_for_email(order):
    """
    Format order data for email templates
    """
    return {
        'order_number': order.order_number,
        'date': order.date.strftime('%B %d, %Y at %I:%M %p'),
        'customer_name': order.full_name,
        'customer_email': order.email,
        'delivery_address': f"{order.street_address1}, {order.town_or_city}, {order.postcode}, {order.country}",
        'items': [
            {
                'name': item.product.name,
                'size': item.size.display_name if item.size else 'N/A',
                'quantity': item.quantity,
                'price': f"€{item.product.price:.2f}",
                'total': f"€{item.lineitem_total:.2f}",
            }
            for item in order.lineitems.all()
        ],
        'subtotal': f"€{order.order_total:.2f}",
        'delivery': f"€{order.delivery_cost:.2f}",
        'total': f"€{order.grand_total:.2f}",
    }