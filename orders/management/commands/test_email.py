"""
Management command to test email functionality
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order
from orders.emails import send_order_confirmation_email, send_order_status_update_email


class Command(BaseCommand):
    help = 'Test email functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
            default='test@example.com'
        )
        parser.add_argument(
            '--order-id',
            type=str,
            help='Order ID to use for testing (optional)'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['basic', 'confirmation', 'status'],
            default='basic',
            help='Type of email test to perform'
        )

    def handle(self, *args, **options):
        email = options['email']
        test_type = options['type']
        
        self.stdout.write(f"Testing email functionality...")
        self.stdout.write(f"Email backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Default from email: {settings.DEFAULT_FROM_EMAIL}")
        
        if test_type == 'basic':
            self.test_basic_email(email)
        elif test_type == 'confirmation':
            self.test_confirmation_email(options.get('order_id'), email)
        elif test_type == 'status':
            self.test_status_email(options.get('order_id'), email)

    def test_basic_email(self, email):
        """Test basic email sending"""
        self.stdout.write("Testing basic email sending...")
        
        try:
            send_mail(
                subject=f"{settings.EMAIL_SUBJECT_PREFIX}Email Test",
                message="This is a test email from Wiesbaden Cyclery.\n\n🚴 Email system is working correctly!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message="""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                        <h1>🚴 Wiesbaden Cyclery</h1>
                        <p>Email Test</p>
                    </div>
                    <div style="padding: 20px;">
                        <h2>✅ Email Test Successful!</h2>
                        <p>This is a test email from Wiesbaden Cyclery.</p>
                        <p>🚴 Email system is working correctly!</p>
                        <p>Unicode characters are displaying properly: 📧 📞 🚚 ✅ 🎉</p>
                    </div>
                </div>
                """,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Basic email sent successfully to {email}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to send basic email: {str(e)}")
            )

    def test_confirmation_email(self, order_id, email):
        """Test order confirmation email"""
        self.stdout.write("Testing order confirmation email...")
        
        try:
            if order_id:
                order = Order.objects.get(order_number=order_id)
            else:
                # Get the most recent order or create a test message
                order = Order.objects.first()
                if not order:
                    self.stdout.write(
                        self.style.WARNING("No orders found. Create an order first or use --type=basic")
                    )
                    return
            
            # Temporarily change email for testing
            original_email = order.email
            order.email = email
            
            success = send_order_confirmation_email(order)
            
            # Restore original email
            order.email = original_email
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Order confirmation email sent successfully to {email}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Failed to send order confirmation email")
                )
                
        except Order.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Order {order_id} not found")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to send confirmation email: {str(e)}")
            )

    def test_status_email(self, order_id, email):
        """Test order status update email"""
        self.stdout.write("Testing order status update email...")
        
        try:
            if order_id:
                order = Order.objects.get(order_number=order_id)
            else:
                order = Order.objects.first()
                if not order:
                    self.stdout.write(
                        self.style.WARNING("No orders found. Create an order first or use --type=basic")
                    )
                    return
            
            # Temporarily change email for testing
            original_email = order.email
            order.email = email
            
            # Test different status updates
            statuses = ['processing', 'shipped', 'delivered']
            
            for status in statuses:
                order.status = status
                success = send_order_status_update_email(order, old_status='pending')
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Status update email ({status}) sent successfully to {email}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed to send status update email ({status})")
                    )
            
            # Restore original email
            order.email = original_email
                
        except Order.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Order {order_id} not found")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to send status update email: {str(e)}")
            )