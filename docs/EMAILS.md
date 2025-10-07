# 📧 Email System

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
- Sent when order is created
- Contains order details, items, totals
- Includes order tracking link

### Status Updates
- Sent when order status changes
- Processing, Shipped, Delivered
- Status-specific messaging

## Templates

```
templates/emails/
├── base_email.html          # HTML base
├── base_email.txt           # Text base
├── order_confirmation.html  # Order HTML
└── order_confirmation.txt   # Order text
```

## Testing

```bash
# Development mode (console)
# Just run server - emails print to terminal

# Production mode (SMTP)
# Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
python manage.py runserver
```

## Features
- Mobile-optimized templates
- Unicode characters (no images)
- Plain text fallback
- Automatic sending via signals
- Professional branding

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No emails | Check Gmail app password |
| Emails to spam | Verify sender domain |
| Template errors | Check template syntax |
| SMTP errors | Verify Gmail 2FA enabled |
