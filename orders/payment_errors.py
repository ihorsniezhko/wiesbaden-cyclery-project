"""
Comprehensive payment error handling system
"""
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Order, OrderStatusHistory

logger = logging.getLogger(__name__)

# Payment error categories
ERROR_CATEGORIES = {
    'card_errors': [
        'card_declined', 'expired_card', 'incorrect_cvc', 'processing_error',
        'incorrect_number', 'invalid_expiry_month', 'invalid_expiry_year',
        'invalid_cvc', 'insufficient_funds', 'withdrawal_count_limit_exceeded',
        'charge_exceeds_source_limit', 'instant_payouts_unsupported',
        'duplicate_transaction', 'fraudulent', 'generic_decline',
        'invalid_account', 'lost_card', 'merchant_blacklist',
        'new_account_information_available', 'no_action_taken',
        'not_permitted', 'pickup_card', 'pin_try_exceeded',
        'restricted_card', 'revocation_of_all_authorizations',
        'revocation_of_authorization', 'security_violation',
        'service_not_allowed', 'stolen_card', 'stop_payment_order',
        'testmode_decline', 'transaction_not_allowed', 'try_again_later'
    ],
    'network_errors': [
        'network_error', 'timeout', 'connection_error'
    ],
    'api_errors': [
        'api_key_expired', 'missing', 'request_failed', 'rate_limit'
    ],
    'validation_errors': [
        'amount_too_large', 'amount_too_small', 'balance_insufficient',
        'currency_not_supported', 'parameter_invalid_empty',
        'parameter_invalid_integer', 'parameter_invalid_string_blank',
        'parameter_invalid_string_empty', 'parameter_missing',
        'parameter_unknown', 'parameters_exclusive'
    ]
}

# User-friendly error messages
USER_FRIENDLY_MESSAGES = {
    # Card declined errors
    'card_declined': {
        'message': 'Your card was declined. Please try a different payment method or contact your bank.',
        'action': 'try_different_card',
        'severity': 'high'
    },
    'expired_card': {
        'message': 'Your card has expired. Please use a different card.',
        'action': 'update_card',
        'severity': 'high'
    },
    'incorrect_cvc': {
        'message': 'Your card\'s security code is incorrect. Please check and try again.',
        'action': 'retry_payment',
        'severity': 'medium'
    },
    'processing_error': {
        'message': 'There was an error processing your card. Please try again in a few minutes.',
        'action': 'retry_payment',
        'severity': 'medium'
    },
    'incorrect_number': {
        'message': 'Your card number is incorrect. Please check and try again.',
        'action': 'retry_payment',
        'severity': 'medium'
    },
    'insufficient_funds': {
        'message': 'Your card has insufficient funds. Please use a different payment method.',
        'action': 'try_different_card',
        'severity': 'high'
    },
    'fraudulent': {
        'message': 'This payment was declined for security reasons. Please contact your bank or try a different card.',
        'action': 'contact_bank',
        'severity': 'high'
    },
    'lost_card': {
        'message': 'This card has been reported lost. Please use a different payment method.',
        'action': 'try_different_card',
        'severity': 'high'
    },
    'stolen_card': {
        'message': 'This card has been reported stolen. Please use a different payment method.',
        'action': 'try_different_card',
        'severity': 'high'
    },
    'generic_decline': {
        'message': 'Your card was declined. Please contact your card issuer for more information or try a different card.',
        'action': 'contact_bank',
        'severity': 'high'
    },
    
    # Network and technical errors
    'network_error': {
        'message': 'There was a network error. Please check your connection and try again.',
        'action': 'retry_payment',
        'severity': 'medium'
    },
    'timeout': {
        'message': 'The payment request timed out. Please try again.',
        'action': 'retry_payment',
        'severity': 'medium'
    },
    'connection_error': {
        'message': 'Connection error. Please check your internet connection and try again.',
        'action': 'retry_payment',
        'severity': 'medium'
    },
    
    # API errors
    'rate_limit': {
        'message': 'Too many payment attempts. Please wait a few minutes and try again.',
        'action': 'wait_retry',
        'severity': 'medium'
    },
    'api_key_expired': {
        'message': 'Payment system configuration error. Please contact support.',
        'action': 'contact_support',
        'severity': 'critical'
    },
    
    # Validation errors
    'amount_too_large': {
        'message': 'The payment amount is too large. Please contact support for assistance.',
        'action': 'contact_support',
        'severity': 'high'
    },
    'amount_too_small': {
        'message': 'The payment amount is too small. Please add more items to your cart.',
        'action': 'modify_cart',
        'severity': 'medium'
    },
    'currency_not_supported': {
        'message': 'This currency is not supported. Please contact support.',
        'action': 'contact_support',
        'severity': 'high'
    },
    
    # Default fallback
    'unknown': {
        'message': 'An unexpected error occurred. Please try again or contact support if the problem persists.',
        'action': 'retry_or_support',
        'severity': 'medium'
    }
}

class PaymentErrorHandler:
    """
    Comprehensive payment error handling class
    """
    
    def __init__(self, order=None):
        self.order = order
        self.error_log = []
    
    def handle_stripe_error(self, error, context=None):
        """
        Handle Stripe-specific errors with comprehensive logging and user feedback
        """
        error_info = self._extract_error_info(error)
        
        # Log the error
        self._log_error(error_info, context)
        
        # Get user-friendly message
        user_message = self._get_user_friendly_message(error_info)
        
        # Record error in order if available
        if self.order:
            self._record_order_error(error_info, user_message)
        
        # Determine recovery action
        recovery_action = self._determine_recovery_action(error_info)
        
        # Send notifications if critical
        if error_info['severity'] == 'critical':
            self._send_critical_error_notification(error_info, context)
        
        return {
            'success': False,
            'error_code': error_info['code'],
            'error_type': error_info['type'],
            'user_message': user_message['message'],
            'recovery_action': recovery_action,
            'severity': error_info['severity'],
            'retry_allowed': recovery_action in ['retry_payment', 'wait_retry'],
            'technical_details': error_info['technical_message'] if settings.DEBUG else None
        }
    
    def _extract_error_info(self, error):
        """
        Extract comprehensive error information from Stripe error
        """
        error_info = {
            'code': 'unknown',
            'type': 'unknown',
            'message': str(error),
            'technical_message': str(error),
            'severity': 'medium',
            'timestamp': timezone.now(),
            'decline_code': None,
            'charge_id': None,
            'payment_intent_id': None
        }
        
        # Handle Stripe error objects
        if hasattr(error, 'code'):
            error_info['code'] = error.code
        if hasattr(error, 'type'):
            error_info['type'] = error.type
        if hasattr(error, 'user_message'):
            error_info['message'] = error.user_message
        if hasattr(error, 'decline_code'):
            error_info['decline_code'] = error.decline_code
        if hasattr(error, 'charge'):
            error_info['charge_id'] = error.charge
        if hasattr(error, 'payment_intent'):
            error_info['payment_intent_id'] = error.payment_intent.get('id') if error.payment_intent else None
        
        # Categorize error
        error_info['category'] = self._categorize_error(error_info['code'])
        
        # Determine severity
        error_info['severity'] = self._determine_severity(error_info['code'], error_info['type'])
        
        return error_info
    
    def _categorize_error(self, error_code):
        """
        Categorize error by type
        """
        for category, codes in ERROR_CATEGORIES.items():
            if error_code in codes:
                return category
        return 'unknown'
    
    def _determine_severity(self, error_code, error_type):
        """
        Determine error severity
        """
        critical_errors = ['api_key_expired', 'missing', 'fraudulent']
        high_errors = ['card_declined', 'insufficient_funds', 'lost_card', 'stolen_card']
        
        if error_code in critical_errors:
            return 'critical'
        elif error_code in high_errors:
            return 'high'
        elif error_type == 'card_error':
            return 'medium'
        else:
            return 'low'
    
    def _get_user_friendly_message(self, error_info):
        """
        Get user-friendly error message
        """
        error_code = error_info['code']
        
        if error_code in USER_FRIENDLY_MESSAGES:
            return USER_FRIENDLY_MESSAGES[error_code]
        else:
            # Try to match by category
            category = error_info['category']
            if category == 'card_errors':
                return USER_FRIENDLY_MESSAGES['card_declined']
            elif category == 'network_errors':
                return USER_FRIENDLY_MESSAGES['network_error']
            else:
                return USER_FRIENDLY_MESSAGES['unknown']
    
    def _determine_recovery_action(self, error_info):
        """
        Determine appropriate recovery action
        """
        user_message = self._get_user_friendly_message(error_info)
        return user_message['action']
    
    def _log_error(self, error_info, context=None):
        """
        Log error with comprehensive details
        """
        log_message = f"Payment error: {error_info['code']} - {error_info['message']}"
        
        if context:
            log_message += f" | Context: {context}"
        
        if self.order:
            log_message += f" | Order: {self.order.order_number}"
        
        # Log based on severity
        if error_info['severity'] == 'critical':
            logger.critical(log_message, extra={'error_info': error_info})
        elif error_info['severity'] == 'high':
            logger.error(log_message, extra={'error_info': error_info})
        elif error_info['severity'] == 'medium':
            logger.warning(log_message, extra={'error_info': error_info})
        else:
            logger.info(log_message, extra={'error_info': error_info})
        
        # Add to internal error log
        self.error_log.append(error_info)
    
    def _record_order_error(self, error_info, user_message):
        """
        Record error in order for tracking
        """
        if not self.order:
            return
        
        # Add error to order notes
        error_note = f"Payment Error [{error_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}]: " \
                     f"{error_info['code']} - {error_info['message']}"
        
        if self.order.order_notes:
            self.order.order_notes += f"\n\n{error_note}"
        else:
            self.order.order_notes = error_note
        
        # Update payment status if appropriate
        if error_info['severity'] in ['high', 'critical']:
            self.order.payment_status = 'failed'
        
        self.order.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=self.order,
            status=self.order.status,
            notes=f"Payment error: {error_info['code']} - {user_message['message']}"
        )
    
    def _send_critical_error_notification(self, error_info, context=None):
        """
        Send notification for critical errors
        """
        try:
            subject = f"Critical Payment Error - {error_info['code']}"
            
            message = f"""
Critical payment error occurred:

Error Code: {error_info['code']}
Error Type: {error_info['type']}
Message: {error_info['message']}
Timestamp: {error_info['timestamp']}
Order: {self.order.order_number if self.order else 'N/A'}
Context: {context or 'N/A'}

Immediate attention required.
            """
            
            admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
            
        except Exception as e:
            logger.error(f"Failed to send critical error notification: {e}")

def handle_payment_error(error, order=None, context=None):
    """
    Convenience function for handling payment errors
    """
    handler = PaymentErrorHandler(order)
    return handler.handle_stripe_error(error, context)

def get_error_recovery_instructions(error_code):
    """
    Get detailed recovery instructions for an error code
    """
    if error_code in USER_FRIENDLY_MESSAGES:
        error_info = USER_FRIENDLY_MESSAGES[error_code]
        
        instructions = {
            'try_different_card': [
                "Try using a different credit or debit card",
                "Ensure your card is activated and not expired",
                "Contact your bank if you continue to have issues"
            ],
            'update_card': [
                "Check your card expiration date",
                "Use a card that hasn't expired",
                "Contact your bank for a replacement card if needed"
            ],
            'retry_payment': [
                "Double-check your card information",
                "Try the payment again in a few minutes",
                "Ensure you have a stable internet connection"
            ],
            'contact_bank': [
                "Contact your card issuer or bank",
                "Ask them to authorize the payment",
                "Try again after speaking with your bank"
            ],
            'contact_support': [
                "Contact our customer support team",
                "Provide your order number for assistance",
                "We'll help resolve the issue quickly"
            ],
            'wait_retry': [
                "Wait a few minutes before trying again",
                "Too many attempts were made recently",
                "Contact support if the issue persists"
            ],
            'modify_cart': [
                "Add more items to reach the minimum amount",
                "Check our minimum order requirements",
                "Contact support if you need assistance"
            ]
        }
        
        return {
            'message': error_info['message'],
            'action': error_info['action'],
            'instructions': instructions.get(error_info['action'], []),
            'severity': error_info['severity']
        }
    
    return {
        'message': USER_FRIENDLY_MESSAGES['unknown']['message'],
        'action': 'retry_or_support',
        'instructions': [
            "Try the payment again",
            "Check your card information",
            "Contact support if the problem continues"
        ],
        'severity': 'medium'
    }