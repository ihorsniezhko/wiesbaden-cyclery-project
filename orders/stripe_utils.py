import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from decimal import Decimal

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

def create_payment_intent(amount, currency='eur', metadata=None):
    """
    Create a Stripe payment intent
    
    Args:
        amount (Decimal): Amount in euros (will be converted to cents)
        currency (str): Currency code (default: 'eur')
        metadata (dict): Additional metadata for the payment intent
    
    Returns:
        dict: Payment intent data or None if error
    """
    try:
        # Convert amount to cents (Stripe requires amounts in smallest currency unit)
        amount_cents = int(amount * 100)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            automatic_payment_methods={
                'enabled': True,
            },
            metadata=metadata or {},
        )
        
        logger.info(f"Payment intent created: {intent.id} for €{amount}")
        return intent
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        return None

def retrieve_payment_intent(payment_intent_id):
    """
    Retrieve a Stripe payment intent
    
    Args:
        payment_intent_id (str): Payment intent ID
    
    Returns:
        PaymentIntent: Stripe payment intent object or None if error
    """
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error retrieving payment intent {payment_intent_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving payment intent {payment_intent_id}: {str(e)}")
        return None

def confirm_payment_intent(payment_intent_id, payment_method_id=None):
    """
    Confirm a Stripe payment intent
    
    Args:
        payment_intent_id (str): Payment intent ID
        payment_method_id (str): Payment method ID (optional)
    
    Returns:
        PaymentIntent: Confirmed payment intent or None if error
    """
    try:
        confirm_params = {}
        if payment_method_id:
            confirm_params['payment_method'] = payment_method_id
            
        intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            **confirm_params
        )
        
        logger.info(f"Payment intent confirmed: {payment_intent_id}")
        return intent
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error confirming payment intent {payment_intent_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error confirming payment intent {payment_intent_id}: {str(e)}")
        return None

def cancel_payment_intent(payment_intent_id, cancellation_reason=None):
    """
    Cancel a Stripe payment intent
    
    Args:
        payment_intent_id (str): Payment intent ID
        cancellation_reason (str): Reason for cancellation
    
    Returns:
        PaymentIntent: Cancelled payment intent or None if error
    """
    try:
        cancel_params = {}
        if cancellation_reason:
            cancel_params['cancellation_reason'] = cancellation_reason
            
        intent = stripe.PaymentIntent.cancel(
            payment_intent_id,
            **cancel_params
        )
        
        logger.info(f"Payment intent cancelled: {payment_intent_id}")
        return intent
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error cancelling payment intent {payment_intent_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error cancelling payment intent {payment_intent_id}: {str(e)}")
        return None

def handle_payment_intent_webhook(payload, sig_header):
    """
    Handle Stripe payment intent webhook
    
    Args:
        payload (bytes): Webhook payload
        sig_header (str): Stripe signature header
    
    Returns:
        tuple: (success: bool, event: dict or None, error: str or None)
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WH_SECRET
        )
        
        logger.info(f"Webhook received: {event['type']}")
        return True, event, None
        
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        return False, None, "Invalid payload"
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        return False, None, "Invalid signature"
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return False, None, str(e)

def format_stripe_amount(amount_cents, currency='eur'):
    """
    Format Stripe amount (in cents) to display format
    
    Args:
        amount_cents (int): Amount in cents
        currency (str): Currency code
    
    Returns:
        str: Formatted amount string
    """
    amount = Decimal(amount_cents) / 100
    if currency.lower() == 'eur':
        return f"€{amount:.2f}"
    else:
        return f"{amount:.2f} {currency.upper()}"

def get_stripe_error_message(error):
    """
    Get user-friendly error message from Stripe error
    
    Args:
        error: Stripe error object
    
    Returns:
        str: User-friendly error message
    """
    error_messages = {
        'card_declined': 'Your card was declined. Please try a different payment method.',
        'expired_card': 'Your card has expired. Please use a different card.',
        'incorrect_cvc': 'Your card\'s security code is incorrect. Please check and try again.',
        'processing_error': 'An error occurred while processing your card. Please try again.',
        'incorrect_number': 'Your card number is incorrect. Please check and try again.',
        'invalid_expiry_month': 'Your card\'s expiration month is invalid.',
        'invalid_expiry_year': 'Your card\'s expiration year is invalid.',
        'invalid_cvc': 'Your card\'s security code is invalid.',
        'insufficient_funds': 'Your card has insufficient funds.',
        'withdrawal_count_limit_exceeded': 'You have exceeded the balance or credit limit available on your card.',
        'charge_exceeds_source_limit': 'The payment exceeds the maximum amount for your card.',
        'instant_payouts_unsupported': 'Your debit card does not support instant payouts.',
        'duplicate_transaction': 'A payment with identical amount and payment information was submitted very recently.',
        'fraudulent': 'The payment has been declined as Stripe suspects it is fraudulent.',
        'generic_decline': 'Your card was declined. Please contact your card issuer for more information.',
        'invalid_account': 'The account number provided is invalid.',
        'lost_card': 'The payment has been declined because the card is reported lost.',
        'merchant_blacklist': 'The payment has been declined because it matches a value on the Stripe user\'s blocklist.',
        'new_account_information_available': 'Your card was declined. Please contact your card issuer for more information.',
        'no_action_taken': 'The payment could not be processed. Please try again.',
        'not_permitted': 'The payment is not permitted.',
        'pickup_card': 'Your card cannot be used to make this payment (it is possible it has been reported lost or stolen).',
        'pin_try_exceeded': 'The allowable number of PIN tries has been exceeded.',
        'restricted_card': 'Your card cannot be used to make this payment (it is possible it has been restricted).',
        'revocation_of_all_authorizations': 'Your card cannot be used to make this payment (it is possible it has been restricted).',
        'revocation_of_authorization': 'Your card cannot be used to make this payment (it is possible it has been restricted).',
        'security_violation': 'Your card cannot be used to make this payment.',
        'service_not_allowed': 'Your card cannot be used to make this payment.',
        'stolen_card': 'The payment has been declined because the card is reported stolen.',
        'stop_payment_order': 'The payment has been declined because the card issuer has declined the transaction.',
        'testmode_decline': 'Your card was declined (test mode).',
        'transaction_not_allowed': 'Your card cannot be used to make this payment.',
        'try_again_later': 'The payment could not be processed. Please try again later.',
        'withdrawal_count_limit_exceeded': 'You have exceeded the balance or credit limit available on your card.',
    }
    
    if hasattr(error, 'code') and error.code in error_messages:
        return error_messages[error.code]
    elif hasattr(error, 'decline_code') and error.decline_code in error_messages:
        return error_messages[error.decline_code]
    else:
        return 'An error occurred while processing your payment. Please try again or contact support.'

def validate_stripe_configuration():
    """
    Validate that Stripe is properly configured
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    if not settings.STRIPE_PUBLIC_KEY:
        errors.append("STRIPE_PUBLIC_KEY is not configured")
    
    if not settings.STRIPE_SECRET_KEY:
        errors.append("STRIPE_SECRET_KEY is not configured")
    
    if not settings.STRIPE_WH_SECRET:
        errors.append("STRIPE_WH_SECRET is not configured")
    
    # Test API connection
    try:
        stripe.Account.retrieve()
    except stripe.error.AuthenticationError:
        errors.append("Invalid Stripe API keys")
    except Exception as e:
        errors.append(f"Stripe API connection error: {str(e)}")
    
    return len(errors) == 0, errors