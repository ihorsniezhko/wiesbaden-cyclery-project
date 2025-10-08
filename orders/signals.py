"""
Order signals for automatic email notifications
"""
import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order
from .utils import (
    send_order_cancelled_email,
    send_order_processing_email,
    send_order_shipped_email,
    send_order_delivered_email,
    restore_product_stock
)

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    """
    Detect order status changes and trigger appropriate actions
    """
    # Only process if this is an existing order (not a new one)
    if instance.pk:
        try:
            # Get the old order state from database
            old_order = Order.objects.get(pk=instance.pk)
            
            # Only send email if status actually changed
            if old_order.status != instance.status:
                logger.info(f"Order {instance.order_number} status changed from {old_order.status} to {instance.status}")
                
                # Send appropriate email based on new status
                if instance.status == 'processing':
                    send_order_processing_email(instance)
                    
                elif instance.status == 'shipped':
                    send_order_shipped_email(instance)
                    
                elif instance.status == 'delivered':
                    send_order_delivered_email(instance)
                    
                elif instance.status == 'cancelled':
                    send_order_cancelled_email(instance)
                    
                    # Restore product stock when order is cancelled
                    try:
                        restore_product_stock(instance)
                        logger.info(f"Product stock restored for cancelled order {instance.order_number}")
                    except Exception as e:
                        logger.error(f"Error restoring stock for order {instance.order_number}: {str(e)}")
                    
        except Order.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            logger.warning(f"Could not find existing order with pk {instance.pk}")
            pass
