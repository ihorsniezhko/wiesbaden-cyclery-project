from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
import json
from products.models import Product, Category, Size
from shopping_cart.models import Cart, CartItem
from .models import Order, OrderLineItem
from .forms import OrderForm


class OrderModelTest(TestCase):
    """Test order model functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='test_bikes',
            friendly_name='Test Bikes'
        )
        
        self.product = Product.objects.create(
            name='Test Bike',
            description='A test bicycle',
            price=Decimal('100.00'),
            category=self.category,
            sku='TEST001',
            stock_quantity=10
        )

    def test_order_creation(self):
        """Test order creation"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            postcode='12345',
            country='US'
        )
        
        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.full_name, 'Test User')
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.order_total, 0)
        # Empty order should have no delivery cost initially
        self.assertEqual(order.delivery_cost, 0)
        self.assertEqual(order.grand_total, 0)

    def test_order_number_generation(self):
        """Test unique order number generation"""
        order1 = Order.objects.create(
            full_name='Test User 1',
            email='test1@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US'
        )
        
        order2 = Order.objects.create(
            full_name='Test User 2',
            email='test2@example.com',
            street_address1='456 Test Ave',
            town_or_city='Test City',
            country='US'
        )
        
        self.assertNotEqual(order1.order_number, order2.order_number)
        self.assertEqual(len(order1.order_number), 32)
        self.assertEqual(len(order2.order_number), 32)

    def test_order_total_calculation(self):
        """Test order total calculation with line items"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US'
        )
        
        # Add line item
        OrderLineItem.objects.create(
            order=order,
            product=self.product,
            quantity=2
        )
        
        order.refresh_from_db()
        self.assertEqual(order.order_total, Decimal('200.00'))
        self.assertEqual(order.delivery_cost, Decimal('0.00'))  # Free over €50
        self.assertEqual(order.grand_total, Decimal('200.00'))

    def test_delivery_cost_calculation(self):
        """Test delivery cost calculation"""
        # Create cheap product
        cheap_product = Product.objects.create(
            name='Cheap Item',
            price=Decimal('30.00'),
            category=self.category,
            sku='CHEAP001'
        )
        
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US'
        )
        
        # Add cheap item (under €50)
        OrderLineItem.objects.create(
            order=order,
            product=cheap_product,
            quantity=1
        )
        
        order.refresh_from_db()
        self.assertEqual(order.delivery_cost, Decimal('4.99'))
        self.assertEqual(order.grand_total, Decimal('34.99'))

    def test_order_status_badge(self):
        """Test order status badge display"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US',
            status='shipped'
        )
        
        self.assertEqual(order.get_status_display_badge(), 'badge-primary')


class OrderLineItemModelTest(TestCase):
    """Test order line item model functionality"""

    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='test_bikes',
            friendly_name='Test Bikes'
        )
        
        self.product = Product.objects.create(
            name='Test Bike',
            description='A test bicycle',
            price=Decimal('100.00'),
            category=self.category,
            sku='TEST001'
        )
        
        self.size = Size.objects.create(name='M', display_name='Medium')
        
        self.order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US'
        )

    def test_line_item_creation(self):
        """Test line item creation"""
        line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            size=self.size,
            quantity=2
        )
        
        self.assertEqual(line_item.lineitem_total, Decimal('200.00'))
        self.assertEqual(str(line_item), f'SKU {self.product.sku} on order {self.order.order_number} (Medium)')

    def test_line_item_without_size(self):
        """Test line item without size"""
        line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1
        )
        
        self.assertIsNone(line_item.size)
        self.assertEqual(line_item.lineitem_total, Decimal('100.00'))

    def test_line_item_updates_order_total(self):
        """Test that line item creation updates order total"""
        initial_total = self.order.grand_total
        
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1
        )
        
        self.order.refresh_from_db()
        self.assertNotEqual(self.order.grand_total, initial_total)
        self.assertEqual(self.order.order_total, Decimal('100.00'))


class OrderViewsTest(TestCase):
    """Test order views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='test_bikes',
            friendly_name='Test Bikes'
        )
        
        self.product = Product.objects.create(
            name='Test Bike',
            description='A test bicycle',
            price=Decimal('100.00'),
            category=self.category,
            sku='TEST001',
            stock_quantity=10
        )

    def test_checkout_view_empty_cart(self):
        """Test checkout view with empty cart"""
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)  # Redirect to cart

    def test_checkout_view_with_cart(self):
        """Test checkout view with items in cart"""
        # Add item to cart
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Checkout')
        self.assertContains(response, 'Test Bike')

    def test_checkout_post_valid_data(self):
        """Test checkout POST with valid data"""
        # Add item to cart
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        
        form_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'street_address1': '123 Test St',
            'town_or_city': 'Test City',
            'postcode': '12345',
            'country': 'US'
        }
        
        response = self.client.post(reverse('orders:checkout'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect to confirmation
        
        # Check order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.full_name, 'Test User')

    def test_order_confirmation_view(self):
        """Test order confirmation view"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US'
        )
        
        response = self.client.get(
            reverse('orders:order_confirmation', args=[order.order_number])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order Confirmed')
        self.assertContains(response, order.order_number)

    def test_order_history_view_authenticated(self):
        """Test order history view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order History')

    def test_order_history_view_anonymous(self):
        """Test order history view redirects anonymous users"""
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_order_tracking_view_get(self):
        """Test order tracking view GET"""
        response = self.client.get(reverse('orders:order_tracking'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Track Your Order')

    def test_order_tracking_view_post_valid(self):
        """Test order tracking view POST with valid data"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US'
        )
        
        response = self.client.post(reverse('orders:order_tracking'), {
            'order_number': order.order_number,
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)
        self.assertContains(response, 'Order Progress')

    def test_order_tracking_view_post_invalid(self):
        """Test order tracking view POST with invalid data"""
        response = self.client.post(reverse('orders:order_tracking'), {
            'order_number': 'INVALID',
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order not found')

    def test_ajax_order_status(self):
        """Test AJAX order status endpoint"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Test City',
            country='US'
        )
        
        response = self.client.get(
            reverse('orders:ajax_order_status', args=[order.order_number])
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['order_number'], order.order_number)
        self.assertEqual(data['status'], 'pending')


class OrderFormTest(TestCase):
    """Test order forms"""

    def test_order_form_valid_data(self):
        """Test order form with valid data"""
        form_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'street_address1': '123 Test St',
            'town_or_city': 'Test City',
            'postcode': '12345',
            'country': 'US'
        }
        
        form = OrderForm(form_data)
        self.assertTrue(form.is_valid())

    def test_order_form_invalid_data(self):
        """Test order form with invalid data"""
        form_data = {
            'full_name': 'Test',  # Should require first and last name
            'email': 'invalid-email',
            'street_address1': '',  # Required field
            'town_or_city': '',  # Required field
            'country': ''  # Required field
        }
        
        form = OrderForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('street_address1', form.errors)
        self.assertIn('town_or_city', form.errors)
        self.assertIn('country', form.errors)

    def test_order_form_email_cleaning(self):
        """Test order form email cleaning"""
        form_data = {
            'full_name': 'Test User',
            'email': '  TEST@EXAMPLE.COM  ',
            'street_address1': '123 Test St',
            'town_or_city': 'Test City',
            'country': 'US'
        }
        
        form = OrderForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'test@example.com')


class OrderIntegrationTest(TestCase):
    """Test order integration with other systems"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='test_bikes',
            friendly_name='Test Bikes'
        )
        
        self.product = Product.objects.create(
            name='Test Bike',
            description='A test bicycle',
            price=Decimal('100.00'),
            category=self.category,
            sku='TEST001',
            stock_quantity=5
        )

    def test_complete_checkout_workflow(self):
        """Test complete checkout workflow from cart to order"""
        # Add item to cart
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        
        # Verify cart has items
        response = self.client.get('/cart/')
        self.assertContains(response, 'Test Bike')
        
        # Go to checkout
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        
        # Submit checkout form
        form_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'street_address1': '123 Test St',
            'town_or_city': 'Test City',
            'postcode': '12345',
            'country': 'US'
        }
        
        response = self.client.post(reverse('orders:checkout'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.lineitems.count(), 1)
        self.assertEqual(order.lineitems.first().quantity, 2)
        
        # Verify stock was updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)  # 5 - 2
        
        # Verify cart was cleared
        response = self.client.get('/cart/')
        self.assertContains(response, 'Your cart is empty')