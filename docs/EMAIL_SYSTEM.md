# Email System Documentation

## Overview

The Wiesbaden Cyclery email system provides automated email notifications for order confirmations and status updates using Gmail SMTP integration with mobile-optimized templates.

## Features

### ✅ Implemented Features
- **Order Confirmation Emails**: Automatic emails sent when orders are created
- **Status Update Emails**: Notifications for order status changes (processing, shipped, delivered)
- **Mobile-Optimized Templates**: Unicode characters only, no graphics for mobile compatibility
- **Dual Backend Support**: SMTP when credentials available, console for development
- **Professional Branding**: Consistent Wiesbaden Cyclery styling and messaging

## Configuration

### Email Settings

The email system uses the exact SMTP configuration from the original wiesbaden_cyclery project:

```python
# Email settings - Use SMTP if credentials are provided, otherwise console
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    # SMTP configuration (works in both development and production)
    EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'info@wiesbaden-cyclery.de')
else:
    # Fallback: Print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'info@wiesbaden-cyclery.de'

# Email configuration for both environments
EMAIL_SUBJECT_PREFIX = '[Wiesbaden Cyclery] '
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

### Environment Variables

Add these to your `.env` file:

```env
# Email settings (Gmail SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=info@wiesbaden-cyclery.de
```

**Note**: Leave `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` empty to use console backend for development.

## Email Templates

### Template Structure

```
templates/emails/
├── base_email.html          # HTML base template
├── base_email.txt           # Text base template
├── order_confirmation.html  # Order confirmation HTML
└── order_confirmation.txt   # Order confirmation text
```

### Mobile Compatibility

All email templates follow mobile-first design principles:

- **Unicode Characters Only**: 🚴 📧 📞 🚚 ✅ (no images or graphics)
- **Responsive Design**: Optimized for mobile devices
- **Plain Text Fallback**: Text versions for all HTML emails
- **Minimal Styling**: Inline CSS for maximum compatibility

## Email Types

### 1. Order Confirmation Email

**Trigger**: Automatically sent when an order is created
**Content**:
- ✅ Order confirmation message
- 📋 Complete order details (items, totals, delivery address)
- 🔍 Order tracking link
- 📞 Next steps and contact information

### 2. Order Status Update Emails

**Triggers**: Sent when order status changes to:
- **Processing**: ⚙️ Order being prepared
- **Shipped**: 🚚 Order in transit
- **Delivered**: ✅ Order successfully delivered

**Content**:
- Status-specific messaging
- Order details and tracking link
- Next steps based on current status

## Usage

### Sending Emails Programmatically

```python
from orders.emails import send_order_confirmation_email, send_order_status_update_email

# Send order confirmation
success = send_order_confirmation_email(order)

# Send status update
success = send_order_status_update_email(order, old_status='pending')
```

### Automatic Email Sending

Emails are sent automatically via Django signals:

- **Order Creation**: Confirmation email sent in checkout view
- **Status Changes**: Update emails sent via `post_save` signal

## Testing

### Run Email Tests

```bash
# Run all email tests
python manage.py test orders.test_emails

# Run specific test class
python manage.py test orders.test_emails.OrderConfirmationEmailTest
```

### Test Email Sending

```bash
# Test basic email functionality
python manage.py test_email --type=basic --email=your-email@example.com

# Test order confirmation email
python manage.py test_email --type=confirmation --email=your-email@example.com

# Test status update emails
python manage.py test_email --type=status --email=your-email@example.com
```

## Development vs Production

### Development Mode
- **Backend**: Console backend (prints emails to terminal)
- **Configuration**: No SMTP credentials required
- **Testing**: All emails visible in console output

### Production Mode
- **Backend**: Gmail SMTP backend
- **Configuration**: Requires Gmail app password
- **Security**: TLS encryption, secure authentication

## Gmail SMTP Setup

### 1. Enable 2-Factor Authentication
Enable 2FA on your Gmail account.

### 2. Generate App Password
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate password for "Mail"
4. Use this password as `EMAIL_HOST_PASSWORD`

### 3. Environment Configuration

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=info@wiesbaden-cyclery.de
```

## Troubleshooting

### Common Issues

1. **Emails not sending in development**
   - Check that `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set
   - Verify Gmail app password is correct
   - Check console output for error messages

2. **Emails going to spam**
   - Verify `DEFAULT_FROM_EMAIL` domain
   - Check email content for spam triggers
   - Consider SPF/DKIM records for production domain

3. **Template rendering errors**
   - Check template syntax
   - Verify context variables are available
   - Test with `python manage.py test_email`

### Logging

Email sending is logged at INFO level:
- Successful sends: `Order confirmation email sent successfully`
- Failures: `Failed to send order confirmation email`

Check Django logs for email delivery status.

## Security Considerations

- **Email Verification**: Order tracking requires email verification
- **No Sensitive Data**: Emails contain only necessary order information
- **Secure SMTP**: TLS encryption for all email transmission
- **App Passwords**: Use Gmail app passwords, not account passwords

## Future Enhancements

Potential improvements for future development:
- Email templates with more advanced styling
- Email delivery status tracking
- Unsubscribe functionality
- Email preferences management
- Automated email campaigns