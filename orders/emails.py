"""
Email utilities for order notifications
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
    try:
        # Get current site for URLs
        current_site = Site.objects.get_current()
        site_url = f"https://{current_site.domain}" if not settings.DEBUG else f"http://{current_site.domain}:8000"
        
        # Email context
        context = {
            'order': order,
            'site_url': site_url,
        }
        
        # Render email templates
        subject = f"{settings.EMAIL_SUBJECT_PREFIX}Order Confirmation - {order.order_number}"
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_message = render_to_string('emails/order_confirmation.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order confirmation email sent successfully for order {order.order_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order {order.order_number}: {str(e)}")
        return False


def send_order_status_update_email(order, old_status=None):
    """
    Send order status update email to customer
    """
    try:
        # Only send email for meaningful status changes
        status_messages = {
            'processing': {
                'subject_suffix': 'Order Processing',
                'title': '⚙️ Order Processing',
                'message': 'Great news! Your order is now being processed and prepared for shipment.',
                'next_steps': [
                    '📦 Your items are being carefully prepared',
                    '🚚 You\'ll receive tracking info once shipped',
                    '📞 Contact us if you have any questions'
                ]
            },
            'shipped': {
                'subject_suffix': 'Order Shipped',
                'title': '🚚 Order Shipped',
                'message': 'Excellent! Your order has been shipped and is on its way to you.',
                'next_steps': [
                    '📦 Your package is in transit',
                    '🔍 Track your package using the provided tracking number',
                    '📅 Expected delivery within 3-5 business days'
                ]
            },
            'delivered': {
                'subject_suffix': 'Order Delivered',
                'title': '✅ Order Delivered',
                'message': 'Wonderful! Your order has been successfully delivered.',
                'next_steps': [
                    '🎉 Enjoy your new bicycle gear!',
                    '⭐ We\'d love to hear about your experience',
                    '🛠️ Contact us if you need any support'
                ]
            }
        }
        
        # Skip if status not in our notification list
        if order.status not in status_messages:
            return True
            
        # Skip if status hasn't actually changed
        if old_status == order.status:
            return True
        
        # Get current site for URLs
        current_site = Site.objects.get_current()
        site_url = f"https://{current_site.domain}" if not settings.DEBUG else f"http://{current_site.domain}:8000"
        
        status_info = status_messages[order.status]
        
        # Email context
        context = {
            'order': order,
            'site_url': site_url,
            'status_info': status_info,
            'old_status': old_status,
        }
        
        # Render email content
        subject = f"{settings.EMAIL_SUBJECT_PREFIX}{status_info['subject_suffix']} - {order.order_number}"
        
        # Create simple HTML email
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h1>🚴 Wiesbaden Cyclery</h1>
                <p>Order Status Update</p>
            </div>
            
            <div style="padding: 30px 20px;">
                <h2>{status_info['title']}</h2>
                
                <p>Dear {order.full_name},</p>
                
                <p>{status_info['message']}</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3>📋 Order Details</h3>
                    <p><strong>Order Number:</strong> {order.order_number}</p>
                    <p><strong>Status:</strong> {order.get_status_display()}</p>
                    <p><strong>Total:</strong> €{order.grand_total}</p>
                </div>
                
                <h3>📞 What's Next?</h3>
                <ul>
                    {''.join([f'<li>{step}</li>' for step in status_info['next_steps']])}
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{site_url}/orders/tracking/" 
                       style="display: inline-block; padding: 12px 24px; background-color: #3498db; 
                              color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        🔍 Track Your Order
                    </a>
                </div>
                
                <p>Thank you for choosing Wiesbaden Cyclery!</p>
                
                <p>Best regards,<br>
                <strong>The Wiesbaden Cyclery Team</strong></p>
            </div>
            
            <div style="background-color: #ecf0f1; padding: 20px; text-align: center; font-size: 14px; color: #7f8c8d;">
                <p><strong>Wiesbaden Cyclery</strong></p>
                <p>📧 info@wiesbaden-cyclery.de | 📞 +49 (0) 611 123456</p>
            </div>
        </div>
        """
        
        # Create plain text version
        plain_message = f"""
{status_info['title']}

Dear {order.full_name},

{status_info['message']}

📋 ORDER DETAILS
================
Order Number: {order.order_number}
Status: {order.get_status_display()}
Total: €{order.grand_total}

📞 WHAT'S NEXT?
===============
{chr(10).join([f'• {step}' for step in status_info['next_steps']])}

🔍 TRACK YOUR ORDER
===================
Visit: {site_url}/orders/tracking/

Thank you for choosing Wiesbaden Cyclery!

Best regards,
The Wiesbaden Cyclery Team

---
Wiesbaden Cyclery
📧 info@wiesbaden-cyclery.de
📞 +49 (0) 611 123456
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order status update email sent successfully for order {order.order_number} (status: {order.status})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order status update email for order {order.order_number}: {str(e)}")
        return False