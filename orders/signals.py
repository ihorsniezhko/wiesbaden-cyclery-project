"""
Django signals for order email notifications
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order
from .emails import send_order_status_update_email
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Track order status changes to send appropriate emails
    """
    if instance.pk:  # Only for existing orders (updates)
        try:
            # Get the old instance from database
            old_instance = Order.objects.get(pk=instance.pk)
            # Store old status for comparison
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def send_status_update_email(sender, instance, created, **kwargs):
    """
    Send status update email when order status changes
    """
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status
        
        # Only send email if status actually changed
        if old_status != new_status:
            logger.info(f"Order {instance.order_number} status changed from {old_status} to {new_status}")
            send_order_status_update_email(instance, old_status)