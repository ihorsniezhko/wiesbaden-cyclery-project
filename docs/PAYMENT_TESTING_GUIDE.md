# Payment System Testing Guide

## Quick Test Commands

```bash
# Run all payment tests
python manage.py test orders

# Test Stripe configuration
python manage.py validate_stripe

# Test webhook system
python manage.py test_webhooks

# Test error handling
python test_payment_errors.py

# Test complete integration
python test_stripe_integration.py
```

## Test Cards (Stripe Test Mode)

- **Success**: 4242 4242 4242 4242
- **Declined**: 4000 0000 0000 0002
- **Insufficient Funds**: 4000 0000 0000 9995
- **Expired**: 4000 0000 0000 0069
- **CVC Fail**: 4000 0000 0000 0127

## Manual Testing Checklist

### 1. Basic Payment Flow
- [ ] Add items to cart
- [ ] Access checkout page
- [ ] Fill order form
- [ ] Enter test card details
- [ ] Complete payment
- [ ] Verify order confirmation
- [ ] Check confirmation email

### 2. Error Scenarios
- [ ] Test declined card
- [ ] Test expired card
- [ ] Test insufficient funds
- [ ] Test network errors
- [ ] Verify error messages
- [ ] Test recovery options

### 3. Webhook Testing
- [ ] Start Stripe CLI: `stripe listen --forward-to localhost:8000/orders/wh/`
- [ ] Process test payment
- [ ] Verify webhook received
- [ ] Check order status update
- [ ] Verify email notifications

### 4. Security Testing
- [ ] Test CSRF protection
- [ ] Test authentication
- [ ] Test order access permissions
- [ ] Test webhook signature verification

## Expected Results

All tests should pass with comprehensive coverage of payment scenarios.