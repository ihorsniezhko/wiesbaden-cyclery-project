from django.core.management.base import BaseCommand
from django.conf import settings
from orders.stripe_utils import validate_stripe_configuration
from orders.webhooks import get_webhook_events

class Command(BaseCommand):
    help = 'Validate Stripe configuration and display setup information'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Stripe Configuration Validation ===\n'))
        
        # Validate configuration
        is_valid, errors = validate_stripe_configuration()
        
        if is_valid:
            self.stdout.write(self.style.SUCCESS('✓ Stripe configuration is valid'))
        else:
            self.stdout.write(self.style.ERROR('✗ Stripe configuration has errors:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        # Display configuration info
        self.stdout.write('\n=== Configuration Details ===')
        self.stdout.write(f'Currency: {settings.STRIPE_CURRENCY.upper()}')
        self.stdout.write(f'Public Key: {settings.STRIPE_PUBLIC_KEY[:12]}...' if settings.STRIPE_PUBLIC_KEY else 'Not configured')
        self.stdout.write(f'Secret Key: {settings.STRIPE_SECRET_KEY[:12]}...' if settings.STRIPE_SECRET_KEY else 'Not configured')
        self.stdout.write(f'Webhook Secret: {settings.STRIPE_WH_SECRET[:12]}...' if settings.STRIPE_WH_SECRET else 'Not configured')
        
        # Display webhook information
        self.stdout.write('\n=== Webhook Configuration ===')
        self.stdout.write('Required webhook events:')
        for event in get_webhook_events():
            self.stdout.write(f'  - {event}')
        
        self.stdout.write(f'\nWebhook endpoint URL: /orders/webhook/stripe/')
        
        # Display setup instructions
        self.stdout.write('\n=== Setup Instructions ===')
        self.stdout.write('1. Create a Stripe account at https://stripe.com')
        self.stdout.write('2. Get your API keys from the Stripe dashboard')
        self.stdout.write('3. Add the keys to your .env file:')
        self.stdout.write('   STRIPE_PUBLIC_KEY=pk_test_...')
        self.stdout.write('   STRIPE_SECRET_KEY=sk_test_...')
        self.stdout.write('4. Create a webhook endpoint in Stripe dashboard:')
        self.stdout.write('   URL: https://yourdomain.com/orders/webhook/stripe/')
        self.stdout.write('   Events: payment_intent.succeeded, payment_intent.payment_failed, etc.')
        self.stdout.write('5. Add the webhook secret to your .env file:')
        self.stdout.write('   STRIPE_WH_SECRET=whsec_...')
        
        if not is_valid:
            self.stdout.write(self.style.ERROR('\nPlease fix the configuration errors before using Stripe payments.'))
        else:
            self.stdout.write(self.style.SUCCESS('\nStripe is ready to use! 🎉'))