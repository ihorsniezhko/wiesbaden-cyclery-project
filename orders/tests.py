"""
Comprehensive test suite for orders and payment system
"""
import json
from decimal import Decimal
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from accounts.models import UserProfile
from products.models import Product, Category, Size
from shopping_cart.models import Cart, CartItem
from .models import Order, OrderLineItem, OrderStatusHistory
from .payment_errors import PaymentErrorHandler, handle_payment_error
from .stripe_utils import create_payment_intent, validate_stripe_configuration
from .webhooks import handle_payment_succeeded, handle_payment_failed
import stripe


class PaymentSystemTestCase(TestCase):
    """Base test case with common setup for payment tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create user profile
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            default_phone_number='+49123456789',
            default_street_address1='Test Street 123',
            default_town_or_city='Berlin',
            default_postcode='10115',
            default_country='DE'
        )
        
        # Create test products
        self.category = Category.objects.create(
            name='test-bikes',
            friendly_name='Test Bikes'
        )
        
        self.size = Size.objects.create(
            name='M',
            display_name='Medium'
        )
        
        self.product = Product.objects.create(
            category=self.category,
            sku='TEST-BIKE-001',
            name='Test Mountain Bike',
            description='A test mountain bike',
            price=Decimal('299.99'),
            rating=Decimal('4.5'),
            image='test-bike.jpg',
            stock_quantity=10,
            in_stock=True
        )
        self.product.sizes.add(self.size)
        
        # Create test cart
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            size=self.size,
            quantity=1
        )
        
        self.client = Client()


class StripeIntegrationTests(PaymentSystemTestCase):
    """Test Stripe integration functionality"""
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_create):
        """Test successful payment intent creation"""
        # Mock Stripe response
        mock_intent = Mock()
        mock_intent.id = 'pi_test_123456789'
        mock_intent.client_secret = 'pi_test_123456789_secret_test'
        mock_intent.amount = 30499  # €304.99 in cents
        mock_intent.currency = 'eur'
        mock_create.return_value = mock_intent
        
        # Test payment intent creation
        result = create_payment_intent(
            amount=Decimal('304.99'),
            currency='eur',
            metadata={'test': 'true'}
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 'pi_test_123456789')
        self.assertEqual(result.amount, 30499)
        
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_failure(self, mock_create):
        """Test payment intent creation failure"""
        # Mock Stripe error
        mock_create.side_effect = stripe.error.CardError(
            message='Your card was declined.',
            param='card',
            code='card_declined'
        )
        
        # Test payment intent creation failure
        result = create_payment_intent(
            amount=Decimal('304.99'),
            currency='eur'
        )
        
        self.assertIsNone(result)
    
    def test_stripe_configuration_validation(self):
        """Test Stripe configuration validation"""
        is_valid, errors = validate_stripe_configuration()
        
        # Should be valid in test environment
        self.assertTrue(is_valid or len(errors) <= 1)  # Allow for debug mode warning


class PaymentErrorHandlingTests(PaymentSystemTestCase):
    """Test payment error handling system"""
    
    def test_error_handler_initialization(self):
        """Test PaymentErrorHandler initialization"""
        handler = PaymentErrorHandler()
        self.assertIsNotNone(handler)
        self.assertEqual(len(handler.error_log), 0)
        
        # Test with order
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            phone_number='+49123456789',
            street_address1='Test Street 123',
            town_or_city='Berlin',
            postcode='10115',
            country='DE',
            order_total=Decimal('304.99'),
            delivery_cost=Decimal('4.99'),
            grand_total=Decimal('309.98')
        )
        
        handler_with_order = PaymentErrorHandler(order)
        self.assertEqual(handler_with_order.order, order)
    
    def test_stripe_error_handling(self):
        """Test Stripe error handling"""
        handler = PaymentErrorHandler()
        
        # Create mock Stripe error
        mock_error = Mock()
        mock_error.code = 'card_declined'
        mock_error.type = 'card_error'
        mock_error.user_message = 'Your card was declined.'
        
        result = handler.handle_stripe_error(mock_error, context='test')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'card_declined')
        self.assertIn('declined', result['user_message'].lower())
        self.assertEqual(result['recovery_action'], 'try_different_card')
        self.assertTrue(result['retry_allowed'])
    
    def test_error_categorization(self):
        """Test error categorization"""
        handler = PaymentErrorHandler()
        
        # Test card error categorization
        self.assertEqual(handler._categorize_error('card_declined'), 'card_errors')
        self.assertEqual(handler._categorize_error('network_error'), 'network_errors')
        self.assertEqual(handler._categorize_error('api_key_expired'), 'api_errors')
        self.assertEqual(handler._categorize_error('unknown_error'), 'unknown')
    
    def test_severity_determination(self):
        """Test error severity determination"""
        handler = PaymentErrorHandler()
        
        self.assertEqual(handler._determine_severity('api_key_expired', 'authentication_error'), 'critical')
        self.assertEqual(handler._determine_severity('card_declined', 'card_error'), 'high')
        self.assertEqual(handler._determine_severity('incorrect_cvc', 'card_error'), 'medium')


class OrderModelTests(PaymentSystemTestCase):
    """Test Order model functionality"""
    
    def test_order_creation(self):
        """Test order creation"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            phone_number='+49123456789',
            street_address1='Test Street 123',
            town_or_city='Berlin',
            postcode='10115',
            country='DE',
            order_total=Decimal('299.99'),
            delivery_cost=Decimal('4.99'),
            grand_total=Decimal('304.98')
        )
        
        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.payment_status, 'pending')
        self.assertEqual(order.grand_total, Decimal('304.98'))
    
    def test_order_number_generation(self):
        """Test unique order number generation"""
        order1 = Order.objects.create(
            full_name='Test User 1',
            email='test1@example.com',
            street_address1='Test Street 123',
            town_or_city='Berlin',
            country='DE'
        )
        
        order2 = Order.objects.create(
            full_name='Test User 2',
            email='test2@example.com',
            street_address1='Test Street 456',
            town_or_city='Munich',
            country='DE'
        )
        
        self.assertNotEqual(order1.order_number, order2.order_number)
        self.assertTrue(len(order1.order_number) > 0)
        self.assertTrue(len(order2.order_number) > 0)
    
    def test_order_total_calculation(self):
        """Test order total calculation"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='Test Street 123',
            town_or_city='Berlin',
            country='DE'
        )
        
        # Add line items
        OrderLineItem.objects.create(
            order=order,
            product=self.product,
            size=self.size,
            quantity=2
        )
        
        order.update_total()
        
        expected_total = self.product.price * 2
        expected_delivery = Decimal('4.99') if expected_total < 50 else Decimal('0.00')
        expected_grand_total = expected_total + expected_delivery
        
        self.assertEqual(order.order_total, expected_total)
        self.assertEqual(order.delivery_cost, expected_delivery)
        self.assertEqual(order.grand_total, expected_grand_total)


class OrderLineItemTests(PaymentSystemTestCase):
    """Test OrderLineItem model functionality"""
    
    def test_line_item_creation(self):
        """Test order line item creation"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='Test Street 123',
            town_or_city='Berlin',
            country='DE'
        )
        
        line_item = OrderLineItem.objects.create(
            order=order,
            product=self.product,
            size=self.size,
            quantity=2
        )
        
        expected_total = self.product.price * 2
        self.assertEqual(line_item.lineitem_total, expected_total)
        self.assertEqual(line_item.product_name, self.product.name)
        self.assertEqual(line_item.product_sku, self.product.sku)
        self.assertEqual(line_item.product_price, self.product.price)


class CheckoutViewTests(PaymentSystemTestCase):
    """Test checkout view functionality"""
    
    def test_checkout_page_access(self):
        """Test checkout page access with cart"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Checkout')
        self.assertContains(response, self.product.name)
    
    def test_checkout_empty_cart_redirect(self):
        """Test checkout redirect with empty cart"""
        # Clear cart
        self.cart.items.all().delete()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('orders:checkout'))
        
        self.assertEqual(response.status_code, 302)  # Redirect
    
    @patch('orders.views.create_payment_intent')
    def test_create_payment_intent_view(self, mock_create_intent):
        """Test payment intent creation view"""
        # Mock successful payment intent creation
        mock_intent = Mock()
        mock_intent.id = 'pi_test_123456789'
        mock_intent.client_secret = 'pi_test_123456789_secret_test'
        mock_create_intent.return_value = mock_intent
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('orders:ajax_create_payment_intent'),
            data=json.dumps({
                'full_name': 'Test User',
                'email': 'test@example.com'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['payment_intent_id'], 'pi_test_123456789')


class WebhookTests(PaymentSystemTestCase):
    """Test webhook functionality"""
    
    def test_payment_succeeded_handler(self):
        """Test payment succeeded webhook handler"""
        # Create order with payment intent
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='Test Street 123',
            town_or_city='Berlin',
            country='DE',
            payment_intent_id='pi_test_123456789',
            order_total=Decimal('299.99'),
            delivery_cost=Decimal('4.99'),
            grand_total=Decimal('304.98')
        )
        
        # Mock payment intent data
        payment_intent_data = {
            'id': 'pi_test_123456789',
            'amount_received': 30498,  # €304.98 in cents
            'currency': 'eur',
            'charges': {
                'data': [{'id': 'ch_test_123456789'}]
            }
        }
        
        result = handle_payment_succeeded(payment_intent_data)
        
        self.assertTrue(result['success'])
        
        # Refresh order from database
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'succeeded')
        self.assertEqual(order.status, 'processing')
    
    def test_payment_failed_handler(self):
        """Test payment failed webhook handler"""
        # Create order with payment intent
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='Test Street 123',
            town_or_city='Berlin',
            country='DE',
            payment_intent_id='pi_test_failed_123',
            order_total=Decimal('299.99'),
            delivery_cost=Decimal('4.99'),
            grand_total=Decimal('304.98')
        )
        
        # Mock failed payment intent data
        payment_intent_data = {
            'id': 'pi_test_failed_123',
            'last_payment_error': {
                'code': 'card_declined',
                'message': 'Your card was declined.',
                'decline_code': 'generic_decline'
            }
        }
        
        result = handle_payment_failed(payment_intent_data)
        
        self.assertTrue(result['success'])
        
        # Refresh order from database
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'failed')
        self.assertIn('card_declined', order.order_notes)


class PaymentIntegrationTests(PaymentSystemTestCase):
    """Integration tests for complete payment flow"""
    
    @patch('orders.views.create_payment_intent')
    @patch('orders.utils.send_order_confirmation_email')
    @patch('orders.utils.send_order_notification_email')
    def test_complete_payment_flow(self, mock_notify, mock_confirm, mock_create_intent):
        """Test complete payment flow from cart to order"""
        # Mock payment intent creation
        mock_intent = Mock()
        mock_intent.id = 'pi_test_integration_123'
        mock_intent.client_secret = 'pi_test_integration_123_secret'
        mock_create_intent.return_value = mock_intent
        
        # Mock email sending
        mock_confirm.return_value = True
        mock_notify.return_value = True
        
        self.client.login(username='testuser', password='testpass123')
        
        # Step 1: Create payment intent
        response = self.client.post(
            reverse('orders:ajax_create_payment_intent'),
            data=json.dumps({
                'full_name': 'Test User',
                'email': 'test@example.com',
                'phone_number': '+49123456789',
                'street_address1': 'Test Street 123',
                'town_or_city': 'Berlin',
                'postcode': '10115',
                'country': 'DE'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        intent_data = json.loads(response.content)
        self.assertTrue(intent_data['success'])
        
        # Step 2: Process payment (simulate successful payment)
        response = self.client.post(
            reverse('orders:ajax_process_payment'),
            data=json.dumps({
                'payment_intent_id': 'pi_test_integration_123',
                'order_form': {
                    'full_name': 'Test User',
                    'email': 'test@example.com',
                    'phone_number': '+49123456789',
                    'street_address1': 'Test Street 123',
                    'town_or_city': 'Berlin',
                    'postcode': '10115',
                    'country': 'DE'
                }
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        process_data = json.loads(response.content)
        self.assertTrue(process_data['success'])
        
        # Verify order was created
        order = Order.objects.get(payment_intent_id='pi_test_integration_123')
        self.assertEqual(order.full_name, 'Test User')
        self.assertEqual(order.payment_status, 'processing')
        
        # Verify cart was cleared
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)


class PaymentSecurityTests(PaymentSystemTestCase):
    """Test payment security features"""
    
    def test_csrf_protection(self):
        """Test CSRF protection on payment endpoints"""
        # Test without CSRF token
        response = self.client.post(
            reverse('orders:ajax_create_payment_intent'),
            data=json.dumps({'test': 'data'}),
            content_type='application/json'
        )
        
        # Should be forbidden due to CSRF protection
        self.assertEqual(response.status_code, 403)
    
    def test_authentication_required(self):
        """Test authentication requirements"""
        # Test order history without authentication
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_order_access_permissions(self):
        """Test order access permissions"""
        # Create order for different user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_profile = UserProfile.objects.create(user=other_user)
        
        order = Order.objects.create(
            user_profile=other_profile,
            full_name='Other User',
            email='other@example.com',
            street_address1='Other Street 123',
            town_or_city='Munich',
            country='DE'
        )
        
        # Login as first user and try to access other user's order
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('orders:order_detail', args=[order.order_number])
        )
        
        self.assertEqual(response.status_code, 403)  # Forbidden