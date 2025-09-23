from django.core.management.base import BaseCommand
from django.conf import settings
from orders.webhooks import validate_webhook_configuration, get_webhook_events
import requests
import json

class Command(BaseCommand):
    help = 'Test and validate webhook configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-endpoint',
            action='store_true',
            help='Test webhook endpoint accessibility',
        )
        parser.add_argument(
            '--validate-config',
            action='store_true',
            help='Validate webhook configuration',
        )
        parser.add_argument(
            '--list-events',
            action='store_true',
            help='List recommended webhook events',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Webhook Testing and Validation ===\n'))
        
        if options['validate_config'] or not any(options.values()):
            self.validate_configuration()
        
        if options['list_events'] or not any(options.values()):
            self.list_recommended_events()
        
        if options['test_endpoint']:
            self.test_endpoint_accessibility()

    def validate_configuration(self):
        """Validate webhook configuration"""
        self.stdout.write('=== Configuration Validation ===')
        
        config = validate_webhook_configuration()
        
        if config['is_valid']:
            self.stdout.write(self.style.SUCCESS('✓ Webhook configuration is valid'))
        else:
            self.stdout.write(self.style.ERROR('✗ Webhook configuration has issues:'))
            for issue in config['issues']:
                self.stdout.write(self.style.ERROR(f'  - {issue}'))
        
        self.stdout.write(f'\nEndpoint URL: {config["endpoint_url"]}')
        self.stdout.write(f'Test Endpoint URL: {config["test_endpoint_url"]}')
        
        # Display current configuration
        self.stdout.write('\n=== Current Configuration ===')
        self.stdout.write(f'Webhook Secret: {settings.STRIPE_WH_SECRET[:12]}...' if settings.STRIPE_WH_SECRET else 'Not configured')
        self.stdout.write(f'Debug Mode: {settings.DEBUG}')
        self.stdout.write(f'Allowed Hosts: {settings.ALLOWED_HOSTS}')

    def list_recommended_events(self):
        """List recommended webhook events"""
        self.stdout.write('\n=== Recommended Webhook Events ===')
        events = get_webhook_events()
        
        for event in events:
            self.stdout.write(f'  - {event}')
        
        self.stdout.write('\n=== Stripe Dashboard Setup ===')
        self.stdout.write('1. Go to https://dashboard.stripe.com/webhooks')
        self.stdout.write('2. Click "Add endpoint"')
        self.stdout.write('3. Enter your endpoint URL')
        self.stdout.write('4. Select the events listed above')
        self.stdout.write('5. Copy the webhook signing secret to your .env file')

    def test_endpoint_accessibility(self):
        """Test if webhook endpoint is accessible"""
        self.stdout.write('\n=== Endpoint Accessibility Test ===')
        
        # This is a basic test - in production you'd test with actual webhook data
        self.stdout.write('Note: This is a basic connectivity test.')
        self.stdout.write('For full testing, use Stripe CLI: stripe listen --forward-to localhost:8000/orders/wh/')
        
        # Test local endpoint
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            
            if result == 0:
                self.stdout.write(self.style.SUCCESS('✓ Local server appears to be running on port 8000'))
            else:
                self.stdout.write(self.style.WARNING('⚠ Local server not detected on port 8000'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error testing local connectivity: {e}'))
        
        # Provide testing instructions
        self.stdout.write('\n=== Testing Instructions ===')
        self.stdout.write('1. Start your Django server: python manage.py runserver')
        self.stdout.write('2. In another terminal, start Stripe CLI:')
        self.stdout.write('   stripe listen --forward-to localhost:8000/orders/wh/')
        self.stdout.write('3. Test with a payment in your application')
        self.stdout.write('4. Check Django logs for webhook processing messages')
        
        self.stdout.write('\n=== Troubleshooting ===')
        self.stdout.write('- Ensure STRIPE_WH_SECRET matches the CLI output')
        self.stdout.write('- Check Django logs for webhook errors')
        self.stdout.write('- Verify ALLOWED_HOSTS includes your domain')
        self.stdout.write('- For production, use ngrok or similar for HTTPS')