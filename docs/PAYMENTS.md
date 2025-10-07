# 💳 Payment System

## Overview
Stripe integration with EUR currency support, secure checkout, and webhook processing.

## Configuration

```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WH_SECRET=whsec_...
```

## Test Cards

| Card Number | Result |
|-------------|--------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Declined |
| 4000 0000 0000 9995 | Insufficient funds |
| 4000 0000 0000 0069 | Expired |

Use any future expiry date and any 3-digit CVC.

## Payment Flow

1. User fills checkout form
2. Stripe Payment Intent created
3. User enters card details
4. Payment processed via Stripe
5. Order created in database
6. Confirmation email sent
7. Webhook updates order status

## Webhook Setup

1. Go to https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://your-domain.com/orders/webhook/stripe/`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy webhook secret to `STRIPE_WH_SECRET`

## Testing

```bash
# Run payment tests
python manage.py test orders

# Test with Stripe CLI
stripe listen --forward-to localhost:8000/orders/wh/
stripe trigger payment_intent.succeeded
```

## Security Features
- PCI compliance via Stripe Elements
- CSRF protection
- Webhook signature verification
- 3D Secure support
- Fraud detection

## Error Handling
- Card declined → User-friendly message
- Network errors → Retry option
- Validation errors → Clear feedback
- Webhook failures → Automatic retry

## Monitoring
- Check Stripe Dashboard for payment details
- Review webhook logs
- Monitor payment success rates
- Track error patterns
