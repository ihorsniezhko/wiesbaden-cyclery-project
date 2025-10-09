# Email System

## Overview
Gmail SMTP integration for order confirmations and status updates.

## Configuration

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=info@wiesbaden-cyclery.de
```

**Note**: Leave empty for development (emails print to console).

## Gmail Setup

1. Enable 2-Factor Authentication on Gmail
2. Go to: Google Account → Security → App passwords
3. Create app password for "Mail"
4. Use 16-character password as `EMAIL_HOST_PASSWORD`

## Email Types

### Order Confirmation
- Sent on order creation
- Order details, items, totals, tracking link

### Order Processing
- Sent on status → 'processing'
- Preparation confirmation, processing time

### Order Shipped
- Sent on status → 'shipped'
- Shipping confirmation, delivery address, tracking

### Order Delivered
- Sent on status → 'delivered'
- Delivery confirmation, satisfaction message

### Order Cancellation
- Sent on status → 'cancelled'
- Refund information, restores product stock

## Templates

```
templates/emails/
├── base_email.html          # HTML base
├── base_email.txt           # Text base
├── order_confirmation.html  # Order confirmation HTML
├── order_confirmation.txt   # Order confirmation text
├── order_processing.html    # Processing HTML
├── order_processing.txt     # Processing text
├── order_shipped.html       # Shipped HTML
├── order_shipped.txt        # Shipped text
├── order_delivered.html     # Delivered HTML
├── order_delivered.txt      # Delivered text
├── order_cancelled.html     # Cancellation HTML
└── order_cancelled.txt      # Cancellation text
```

## Testing

```bash
# Development mode (console)
# Just run server - emails print to terminal

# Production mode (SMTP)
# Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
python manage.py runserver
```

## Automatic Status Change Emails

All status change emails are sent automatically via Django signals when an order status is updated in:
- Django Admin panel
- Order management views
- API endpoints
- Any code that changes order status

**Status Flow:**
```
Pending → Processing → Shipped → Delivered
         ↓
      Cancelled (restores stock)
```

**Email Triggers:**
- `pending` → No email (initial state)
- `processing` → Processing email sent
- `shipped` → Shipped email sent
- `delivered` → Delivered email sent
- `cancelled` → Cancellation email sent + stock restored

## Features
- Mobile-optimized templates
- Unicode characters (no images)
- Plain text fallback
- Automatic sending via Django signals
- Professional branding
- Status-specific messaging
- Automatic stock restoration on cancellation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No emails | Check Gmail app password |
| Emails to spam | Verify sender domain |
| Template errors | Check template syntax |
| SMTP errors | Verify Gmail 2FA enabled |
