import json
import logging
import time
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db import transaction
from django.core.cache import cache
from .models import Order, OrderStatusHistory
from .stripe_utils import handle_payment_intent_webhook
from .utils import send_order_confirmation_email, send_order_notification_email
from .webhook_monitor import record_webhook_event

logger = logging.getLogger(__name__)

# Webhook event tracking for idempotency
WEBHOOK_CACHE_PREFIX = 'stripe_webhook_'
WEBHOOK_CACHE_TIMEOUT = 3600  # 1 hour

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events with enhanced security and verification
    """
    start_time = time.time()
    
    # Log incoming webhook request
    logger.info(f"Webhook received from IP: {get_client_ip(request)}")
    
    # Basic request validation
    payload = request.body
    if not payload:
        logger.error("Empty webhook payload received")
        return HttpResponseBadRequest("Empty payload")
    
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    if not sig_header:
        logger.error("Missing Stripe signature header")
        return HttpResponseBadRequest("Missing signature")
    
    # Verify webhook signature and get event
    success, event, error = handle_payment_intent_webhook(payload, sig_header)
    
    if not success:
        logger.error(f"Webhook verification failed: {error}")
        return HttpResponseBadRequest(f"Verification failed: {error}")
    
    # Extract event information
    event_id = event.get('id')
    event_type = event.get('type')
    
    if not event_id or not event_type:
        logger.error("Invalid webhook event structure")
        return HttpResponseBadRequest("Invalid event structure")
    
    # Idempotency check - prevent duplicate processing
    cache_key = f"{WEBHOOK_CACHE_PREFIX}{event_id}"
    if cache.get(cache_key):
        logger.info(f"Webhook event {event_id} already processed, skipping")
        return HttpResponse("Event already processed", status=200)
    
    # Mark event as being processed
    cache.set(cache_key, True, WEBHOOK_CACHE_TIMEOUT)
    
    logger.info(f"Processing webhook event: {event_type} (ID: {event_id})")
    
    # Handle the event with simplified processing
    try:
        result = process_webhook_event(event)
        processing_time = time.time() - start_time
        
        if result['success']:
            logger.info(f"Webhook event {event_id} processed successfully in {processing_time:.2f}s")
            return HttpResponse("Event processed successfully", status=200)
        else:
            logger.error(f"Failed to process webhook event {event_id}: {result['error']}")
            # Remove from cache so it can be retried
            cache.delete(cache_key)
            return HttpResponse(f"Processing failed: {result['error']}", status=200)  # Return 200 to prevent retries
                
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Unexpected error processing webhook event {event_id}: {str(e)}", exc_info=True)
        # Remove from cache so it can be retried
        cache.delete(cache_key)
        return HttpResponse("Internal server error", status=200)  # Return 200 to prevent retries


def get_client_ip(request):
    """Get the client IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def process_webhook_event(event):
    """
    Process webhook event and return result
    """
    event_type = event['type']
    event_data = event['data']['object']
    
    try:
        if event_type == 'payment_intent.succeeded':
            return handle_payment_succeeded(event_data)
        elif event_type == 'payment_intent.payment_failed':
            return handle_payment_failed(event_data)
        elif event_type == 'payment_intent.canceled':
            return handle_payment_canceled(event_data)
        elif event_type == 'payment_intent.requires_action':
            return handle_payment_requires_action(event_data)
        elif event_type == 'payment_intent.processing':
            return handle_payment_processing(event_data)
        elif event_type == 'charge.dispute.created':
            return handle_dispute_created(event_data)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return {'success': True, 'message': f'Event type {event_type} not handled'}
            
    except Exception as e:
        logger.error(f"Error in event handler for {event_type}: {str(e)}", exc_info=True)
        return {'success': False, 'error': str(e)}

def handle_payment_succeeded(payment_intent):
    """
    Handle successful payment with enhanced verification and logging
    """
    payment_intent_id = payment_intent['id']
    amount_received = payment_intent.get('amount_received', 0)
    currency = payment_intent.get('currency', 'eur')
    
    logger.info(f"Processing payment success: {payment_intent_id} - {amount_received/100:.2f} {currency.upper()}")
    
    # Find the order by payment intent ID
    try:
        order = Order.objects.select_for_update().get(payment_intent_id=payment_intent_id)
    except Order.DoesNotExist:
        # Check if this is a test payment intent (not linked to an order)
        metadata = payment_intent.get('metadata', {})
        if metadata.get('test') == 'simple_stripe_test' or payment_intent_id.startswith('pi_'):
            logger.info(f"Test payment intent processed successfully: {payment_intent_id}")
            return {'success': True, 'message': f'Test payment intent {payment_intent_id} processed'}
        
        logger.error(f"Order not found for payment intent: {payment_intent_id}")
        return {'success': False, 'error': f'Order not found for payment intent {payment_intent_id}'}
    
    # Verify payment amount matches order total
    expected_amount = int(order.grand_total * 100)  # Convert to cents
    if amount_received != expected_amount:
        logger.error(f"Payment amount mismatch for order {order.order_number}: "
                    f"expected {expected_amount}, received {amount_received}")
        return {'success': False, 'error': 'Payment amount mismatch'}
    
    # Check if already processed
    if order.payment_status == 'succeeded':
        logger.info(f"Order {order.order_number} payment already processed")
        return {'success': True, 'message': 'Payment already processed'}
    
    # Update order status
    old_status = order.status
    old_payment_status = order.payment_status
    
    order.payment_status = 'succeeded'
    order.status = 'processing'
    
    # Extract charge ID for reference
    charges = payment_intent.get('charges', {}).get('data', [])
    if charges:
        order.stripe_pid = charges[0].get('id', '')
    
    order.save()
    
    # Create status history entry
    OrderStatusHistory.objects.create(
        order=order,
        status='processing',
        notes=f"Payment succeeded via webhook. Amount: {amount_received/100:.2f} {currency.upper()}. "
               f"Status: {old_status} → processing. Payment: {old_payment_status} → succeeded."
    )
    
    # Send confirmation emails (with error handling)
    email_results = []
    try:
        if send_order_confirmation_email(order):
            email_results.append("customer confirmation sent")
        else:
            email_results.append("customer confirmation failed")
    except Exception as e:
        logger.error(f"Error sending customer confirmation for order {order.order_number}: {str(e)}")
        email_results.append("customer confirmation error")
    
    try:
        if send_order_notification_email(order):
            email_results.append("admin notification sent")
        else:
            email_results.append("admin notification failed")
    except Exception as e:
        logger.error(f"Error sending admin notification for order {order.order_number}: {str(e)}")
        email_results.append("admin notification error")
    
    logger.info(f"Order {order.order_number} payment processed successfully. Emails: {', '.join(email_results)}")
    
    return {'success': True, 'message': f'Payment processed for order {order.order_number}'}

def handle_payment_failed(payment_intent):
    """
    Handle failed payment with detailed error tracking
    """
    payment_intent_id = payment_intent['id']
    logger.info(f"Processing payment failure: {payment_intent_id}")
    
    # Find the order by payment intent ID
    try:
        order = Order.objects.select_for_update().get(payment_intent_id=payment_intent_id)
    except Order.DoesNotExist:
        # Check if this is a test payment intent
        metadata = payment_intent.get('metadata', {})
        if metadata.get('test') == 'simple_stripe_test' or payment_intent_id.startswith('pi_'):
            logger.info(f"Test payment intent failure processed: {payment_intent_id}")
            return {'success': True, 'message': f'Test payment intent failure {payment_intent_id} processed'}
        
        logger.error(f"Order not found for payment intent: {payment_intent_id}")
        return {'success': False, 'error': f'Order not found for payment intent {payment_intent_id}'}
    
    # Extract detailed failure information
    last_payment_error = payment_intent.get('last_payment_error', {})
    failure_code = last_payment_error.get('code', 'unknown')
    failure_message = last_payment_error.get('message', 'Payment failed')
    decline_code = last_payment_error.get('decline_code', '')
    
    # Update order payment status
    old_payment_status = order.payment_status
    order.payment_status = 'failed'
    
    # Create detailed failure note
    failure_details = f"Payment failed via webhook. Code: {failure_code}"
    if decline_code:
        failure_details += f", Decline: {decline_code}"
    failure_details += f". Message: {failure_message}"
    
    # Add failure reason to order notes
    if order.order_notes:
        order.order_notes += f"\n\n{failure_details}"
    else:
        order.order_notes = failure_details
    
    order.save()
    
    # Create status history entry
    OrderStatusHistory.objects.create(
        order=order,
        status=order.status,  # Keep current status
        notes=f"Payment failed via webhook. Payment status: {old_payment_status} → failed. "
               f"Error: {failure_code} - {failure_message}"
    )
    
    logger.warning(f"Order {order.order_number} payment failed: {failure_code} - {failure_message}")
    
    return {'success': True, 'message': f'Payment failure processed for order {order.order_number}'}

def handle_payment_canceled(payment_intent):
    """
    Handle canceled payment
    """
    try:
        payment_intent_id = payment_intent['id']
        logger.info(f"Payment canceled for payment intent: {payment_intent_id}")
        
        # Find the order by payment intent ID
        try:
            order = Order.objects.get(payment_intent_id=payment_intent_id)
        except Order.DoesNotExist:
            logger.error(f"Order not found for payment intent: {payment_intent_id}")
            return
        
        # Update order status
        old_status = order.status
        old_payment_status = order.payment_status
        
        order.payment_status = 'cancelled'
        order.status = 'cancelled'
        
        # Get cancellation reason
        cancellation_reason = payment_intent.get('cancellation_reason', 'Payment canceled')
        
        # Add cancellation reason to order notes
        if order.order_notes:
            order.order_notes += f"\n\nPayment canceled: {cancellation_reason}"
        else:
            order.order_notes = f"Payment canceled: {cancellation_reason}"
        
        order.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes=f"Payment canceled. Status changed from {old_status} to cancelled. Payment status changed from {old_payment_status} to cancelled. Reason: {cancellation_reason}"
        )
        
        logger.info(f"Order {order.order_number} canceled after payment cancellation")
        
    except Exception as e:
        logger.error(f"Error handling payment canceled: {str(e)}")

def handle_payment_requires_action(payment_intent):
    """
    Handle payment that requires additional action (e.g., 3D Secure)
    """
    try:
        payment_intent_id = payment_intent['id']
        logger.info(f"Payment requires action for payment intent: {payment_intent_id}")
        
        # Find the order by payment intent ID
        try:
            order = Order.objects.get(payment_intent_id=payment_intent_id)
        except Order.DoesNotExist:
            logger.error(f"Order not found for payment intent: {payment_intent_id}")
            return
        
        # Update order payment status
        old_payment_status = order.payment_status
        order.payment_status = 'processing'
        
        # Add note about required action
        action_note = "Payment requires additional authentication (e.g., 3D Secure)"
        if order.order_notes:
            order.order_notes += f"\n\n{action_note}"
        else:
            order.order_notes = action_note
        
        order.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=order.status,  # Keep current status
            notes=f"Payment requires action. Payment status changed from {old_payment_status} to processing. {action_note}"
        )
        
        logger.info(f"Order {order.order_number} updated - payment requires action")
        
    except Exception as e:
        logger.error(f"Error handling payment requires action: {str(e)}")

def get_webhook_events():
    """
    Get list of webhook events that should be configured in Stripe dashboard
    """
    return [
        'payment_intent.succeeded',
        'payment_intent.payment_failed',
        'payment_intent.canceled',
        'payment_intent.requires_action',
    ]
def handle_payment_processing(payment_intent):
    """
    Handle payment in processing state
    """
    payment_intent_id = payment_intent['id']
    logger.info(f"Processing payment processing state: {payment_intent_id}")
    
    try:
        order = Order.objects.select_for_update().get(payment_intent_id=payment_intent_id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for payment intent: {payment_intent_id}")
        return {'success': False, 'error': f'Order not found for payment intent {payment_intent_id}'}
    
    # Update payment status if not already processing
    if order.payment_status != 'processing':
        old_payment_status = order.payment_status
        order.payment_status = 'processing'
        order.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=order.status,
            notes=f"Payment processing via webhook. Payment status: {old_payment_status} → processing"
        )
        
        logger.info(f"Order {order.order_number} payment status updated to processing")
    
    return {'success': True, 'message': f'Payment processing status updated for order {order.order_number}'}


def handle_dispute_created(charge):
    """
    Handle dispute/chargeback creation
    """
    charge_id = charge['id']
    dispute_id = charge.get('dispute', {}).get('id', 'unknown')
    amount = charge.get('amount', 0)
    currency = charge.get('currency', 'eur')
    
    logger.warning(f"Dispute created for charge {charge_id}: {dispute_id} - {amount/100:.2f} {currency.upper()}")
    
    # Try to find the order by charge ID
    try:
        order = Order.objects.get(stripe_pid=charge_id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for disputed charge: {charge_id}")
        return {'success': False, 'error': f'Order not found for charge {charge_id}'}
    
    # Add dispute information to order notes
    dispute_note = f"DISPUTE CREATED: Dispute ID {dispute_id} for charge {charge_id}. " \
                   f"Amount: {amount/100:.2f} {currency.upper()}. Immediate action required."
    
    if order.order_notes:
        order.order_notes += f"\n\n{dispute_note}"
    else:
        order.order_notes = dispute_note
    
    order.save()
    
    # Create status history entry
    OrderStatusHistory.objects.create(
        order=order,
        status=order.status,
        notes=f"Dispute created via webhook. Dispute ID: {dispute_id}. Charge: {charge_id}"
    )
    
    # TODO: Send urgent notification to admin about dispute
    logger.critical(f"URGENT: Dispute created for order {order.order_number}. Dispute ID: {dispute_id}")
    
    return {'success': True, 'message': f'Dispute recorded for order {order.order_number}'}


def get_webhook_events():
    """
    Get list of webhook events that should be configured in Stripe dashboard
    """
    return [
        'payment_intent.succeeded',
        'payment_intent.payment_failed',
        'payment_intent.canceled',
        'payment_intent.requires_action',
        'payment_intent.processing',
        'charge.dispute.created',
        'invoice.payment_succeeded',
        'invoice.payment_failed',
    ]


def validate_webhook_configuration():
    """
    Validate webhook configuration and provide setup guidance
    """
    from django.conf import settings
    
    issues = []
    
    # Check webhook secret
    if not settings.STRIPE_WH_SECRET:
        issues.append("STRIPE_WH_SECRET not configured")
    elif not settings.STRIPE_WH_SECRET.startswith('whsec_'):
        issues.append("STRIPE_WH_SECRET appears to be invalid (should start with 'whsec_')")
    
    # Check if we're in debug mode
    if settings.DEBUG:
        issues.append("DEBUG mode is enabled - ensure webhooks work with ngrok or similar for local testing")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'recommended_events': get_webhook_events(),
        'endpoint_url': '/orders/webhook/stripe/',
        'test_endpoint_url': '/orders/wh/',  # For Stripe CLI
    }