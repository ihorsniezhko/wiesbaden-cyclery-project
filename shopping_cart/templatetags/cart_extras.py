from django import template
from django.conf import settings
from decimal import Decimal

register = template.Library()

@register.filter
def free_delivery_delta(subtotal):
    """Calculate how much more is needed for free delivery"""
    try:
        subtotal_decimal = Decimal(str(subtotal))
        free_delivery_threshold = Decimal(str(settings.FREE_DELIVERY_THRESHOLD))
        delta = max(Decimal('0.00'), free_delivery_threshold - subtotal_decimal)
        return float(delta)
    except (ValueError, TypeError):
        return float(getattr(settings, 'FREE_DELIVERY_THRESHOLD', 50.00))