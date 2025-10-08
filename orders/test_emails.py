"""
Tests for order email functionality
"""
from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from unittest.mock import patch, MagicMock
from decimal import Decimal

from accounts.models import UserProfile
from products.models import Product, Category, Size
from .models import Order, OrderLineItem
from .emails import send_order_confirmation_email, send_order_status_update_email


class EmailTestCase(TestCase):
    """Base test case for email tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create user profile
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            default_phone_number='123456789',
            default_street_address1='123 Test St',
            default_town_or_city='Test City',
            default_postcode='12345',
            default_country='DE'
        )
        
        # Create test product data
        self.category = Category.objects.create(
            name='Test Category',
            friendly_name='Test Category'
        )
        
        self.size = Size.objects.create(name='M')
        
        self.product = Product.objects.create(
            category=self.category,
            sku='TEST001',
            name='Test Product',
            description='Test product description',
            price=Decimal('29.99'),
            rating=4.5,
            image='test.jpg'
        )
        self.product.sizes.add(self.size)
        
        # Create test order
        self.order = Order.objects.create(
            user_profile=self.user_profile,
            full_name='Test User',
            email='test@example.com',
            phone_number='123456789',
            street_address1='123 Test St',
            town_or_city='Test City',
            postcode='12345',
            country='DE',
            order_total=Decimal('29.99'),
            delivery_cost=Decimal('4.99'),
            grand_total=Decimal('34.98'),
            status='pending'
        )
        
        # Create order line item
        self.order_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            product_size=self.size,
            quantity=1,
            lineitem_total=Decimal('29.99')
        )
        
        # Ensure site exists
        Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'testserver', 'name': 'Test Site'}
        )


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class OrderConfirmationEmailTest(EmailTestCase):
    """Test order confirmation emails"""
    
    def test_send_order_confirmation_email_success(self):
        """Test successful order confirmation email sending"""
        # Clear any existing emails
        mail.outbox = []
        
        # Send confirmation email
        result = send_order_confirmation_email(self.order)
        
        # Check result
        self.assertTrue(result)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('[Wiesbaden Cyclery]', email.subject)
        self.assertIn('Order Confirmation', email.subject)
        self.assertIn(self.order.order_number, email.subject)
        self.assertEqual(email.to, [self.order.email])
        self.assertIn('Order Confirmed', email.body)
        self.assertIn(self.order.order_number, email.body)
        self.assertIn(self.order.full_name, email.body)
        
        # Check HTML content
        self.assertIn('✅ Order Confirmed!', email.alternatives[0][0])
        self.assertIn(self.product.name, email.alternatives[0][0])
    
    def test_send_order_confirmation_email_with_multiple_items(self):
        """Test order confirmation email with multiple items"""
        # Add another item to order
        product2 = Product.objects.create(
            category=self.category,
            sku='TEST002',
            name='Test Product 2',
            description='Second test product',
            price=Decimal('49.99'),
            rating=4.0
        )
        
        OrderLineItem.objects.create(
            order=self.order,
            product=product2,
            quantity=2,
            lineitem_total=Decimal('99.98')
        )
        
        # Update order totals
        self.order.order_total = Decimal('129.97')
        self.order.grand_total = Decimal('129.97')  # Free delivery over €50
        self.order.delivery_cost = Decimal('0.00')
        self.order.save()
        
        # Clear any existing emails
        mail.outbox = []
        
        # Send confirmation email
        result = send_order_confirmation_email(self.order)
        
        # Check result
        self.assertTrue(result)
        
        # Check email content includes both products
        email = mail.outbox[0]
        self.assertIn('Test Product', email.body)
        self.assertIn('Test Product 2', email.body)
        self.assertIn('€129.97', email.body)
        self.assertIn('€0.00', email.body)  # Free delivery
    
    @patch('orders.emails.send_mail')
    def test_send_order_confirmation_email_failure(self, mock_send_mail):
        """Test order confirmation email sending failure"""
        # Mock send_mail to raise exception
        mock_send_mail.side_effect = Exception('SMTP Error')
        
        # Send confirmation email
        result = send_order_confirmation_email(self.order)
        
        # Check result
        self.assertFalse(result)
        
        # Verify send_mail was called
        self.assertTrue(mock_send_mail.called)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class OrderStatusUpdateEmailTest(EmailTestCase):
    """Test order status update emails"""
    
    def test_send_status_update_email_processing(self):
        """Test status update email for processing status"""
        # Clear any existing emails
        mail.outbox = []
        
        # Send status update email
        result = send_order_status_update_email(self.order, old_status='pending')
        
        # Update order status to processing
        self.order.status = 'processing'
        result = send_order_status_update_email(self.order, old_status='pending')
        
        # Check result
        self.assertTrue(result)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Order Processing', email.subject)
        self.assertIn(self.order.order_number, email.subject)
        self.assertIn('⚙️ Order Processing', email.body)
        self.assertIn('being processed', email.body)
    
    def test_send_status_update_email_shipped(self):
        """Test status update email for shipped status"""
        # Clear any existing emails
        mail.outbox = []
        
        # Update order status to shipped
        self.order.status = 'shipped'
        result = send_order_status_update_email(self.order, old_status='processing')
        
        # Check result
        self.assertTrue(result)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Order Shipped', email.subject)
        self.assertIn('🚚 Order Shipped', email.body)
        self.assertIn('has been shipped', email.body)
    
    def test_send_status_update_email_delivered(self):
        """Test status update email for delivered status"""
        # Clear any existing emails
        mail.outbox = []
        
        # Update order status to delivered
        self.order.status = 'delivered'
        result = send_order_status_update_email(self.order, old_status='shipped')
        
        # Check result
        self.assertTrue(result)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Order Delivered', email.subject)
        self.assertIn('✅ Order Delivered', email.body)
        self.assertIn('successfully delivered', email.body)
    
    def test_send_status_update_email_no_change(self):
        """Test that no email is sent when status doesn't change"""
        # Clear any existing emails
        mail.outbox = []
        
        # Send status update email with same status
        result = send_order_status_update_email(self.order, old_status='pending')
        
        # Check result (should still be True but no email sent)
        self.assertTrue(result)
        
        # Check no email was sent
        self.assertEqual(len(mail.outbox), 0)
    
    def test_send_status_update_email_invalid_status(self):
        """Test status update email for invalid status"""
        # Clear any existing emails
        mail.outbox = []
        
        # Update order status to cancelled (not in notification list)
        self.order.status = 'cancelled'
        result = send_order_status_update_email(self.order, old_status='pending')
        
        # Check result (should be True but no email sent)
        self.assertTrue(result)
        
        # Check no email was sent
        self.assertEqual(len(mail.outbox), 0)
    
    @patch('orders.emails.send_mail')
    def test_send_status_update_email_failure(self, mock_send_mail):
        """Test status update email sending failure"""
        # Mock send_mail to raise exception
        mock_send_mail.side_effect = Exception('SMTP Error')
        
        # Update order status
        self.order.status = 'processing'
        result = send_order_status_update_email(self.order, old_status='pending')
        
        # Check result
        self.assertFalse(result)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
class EmailBackendTest(EmailTestCase):
    """Test email backend configuration"""
    
    def test_console_backend_fallback(self):
        """Test that console backend is used when SMTP credentials not available"""
        from django.conf import settings
        
        # Check that console backend is configured
        self.assertEqual(settings.EMAIL_BACKEND, 'django.core.mail.backends.console.EmailBackend')
        
        # Send email (should not raise exception)
        result = send_order_confirmation_email(self.order)
        
        # Should succeed even with console backend
        self.assertTrue(result)


class EmailTemplateTest(EmailTestCase):
    """Test email template rendering"""
    
    def test_order_confirmation_template_context(self):
        """Test order confirmation template has correct context"""
        from django.template.loader import render_to_string
        from django.contrib.sites.models import Site
        
        # Get current site
        site = Site.objects.get_current()
        site_url = f"http://{site.domain}:8000"
        
        context = {
            'order': self.order,
            'site_url': site_url,
        }
        
        # Render HTML template
        html_content = render_to_string('emails/order_confirmation.html', context)
        
        # Check content
        self.assertIn('Order Confirmed', html_content)
        self.assertIn(self.order.order_number, html_content)
        self.assertIn(self.order.full_name, html_content)
        self.assertIn(self.product.name, html_content)
        self.assertIn('Track Your Order', html_content)
        
        # Render text template
        text_content = render_to_string('emails/order_confirmation.txt', context)
        
        # Check text content
        self.assertIn('ORDER CONFIRMED', text_content)
        self.assertIn(self.order.order_number, text_content)
        self.assertIn(self.order.full_name, text_content)
    
    def test_base_email_template_unicode_only(self):
        """Test that base email template uses only Unicode characters"""
        from django.template.loader import render_to_string
        
        context = {'order': self.order}
        
        # Render base template
        html_content = render_to_string('emails/base_email.html', context)
        
        # Check for Unicode characters (should be present)
        self.assertIn('🚴', html_content)  # Bicycle emoji
        self.assertIn('📍', html_content)  # Location emoji
        self.assertIn('📧', html_content)  # Email emoji
        self.assertIn('📞', html_content)  # Phone emoji
        
        # Check that no image tags or external graphics are used
        self.assertNotIn('<img', html_content.lower())
        self.assertNotIn('src=', html_content.lower())
        self.assertNotIn('.png', html_content.lower())
        self.assertNotIn('.jpg', html_content.lower())
        self.assertNotIn('.gif', html_content.lower())


class EmailSignalTest(EmailTestCase):
    """Test email signals for status changes"""
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_order_status_change_signal(self):
        """Test that email is sent when order status changes via signal"""
        # Clear any existing emails
        mail.outbox = []
        
        # Change order status (this should trigger signal)
        self.order.status = 'processing'
        self.order.save()
        
        # Check email was sent via signal
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Order Processing', email.subject)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_new_order_no_status_email(self):
        """Test that no status email is sent for new orders"""
        # Clear any existing emails
        mail.outbox = []
        
        # Create new order (should not trigger status change email)
        new_order = Order.objects.create(
            user_profile=self.user_profile,
            full_name='New User',
            email='new@example.com',
            phone_number='987654321',
            street_address1='456 New St',
            town_or_city='New City',
            postcode='54321',
            country='DE',
            order_total=Decimal('19.99'),
            delivery_cost=Decimal('4.99'),
            grand_total=Decimal('24.98'),
            status='pending'
        )
        
        # Check no email was sent (new order, no status change)
        self.assertEqual(len(mail.outbox), 0)