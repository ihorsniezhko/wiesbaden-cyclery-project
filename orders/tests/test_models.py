"""
Tests for Order models
"""
from django.test import TestCase
from decimal import Decimal
from orders.models import Order, OrderLineItem
from products.models import Product, Category


class OrderModelTest(TestCase):
    """Test Order model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='road_bikes',
            friendly_name='Road Bikes'
        )
        self.product = Product.objects.create(
            name='Test Bike',
            price=Decimal('999.99'),
            category=self.category,
            stock_quantity=10,
            in_stock=True
        )
    
    def test_order_creation(self):
        """Test creating an order"""
        order = Order.objects.create(
            full_name='John Doe',
            email='john@example.com',
            phone_number='1234567890',
            street_address1='123 Main St',
            town_or_city='Wiesbaden',
            postcode='65183',
            country='DE'
        )
        self.assertEqual(order.full_name, 'John Doe')
        self.assertEqual(order.email, 'john@example.com')
        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.status, 'pending')
    
    def test_order_number_generation(self):
        """Test order number is automatically generated"""
        order = Order.objects.create(
            full_name='Jane Doe',
            email='jane@example.com',
            street_address1='456 Oak Ave',
            town_or_city='Wiesbaden',
            postcode='65183',
            country='DE'
        )
        self.assertIsNotNone(order.order_number)
        self.assertEqual(len(order.order_number), 32)
    
    def test_order_total_calculation(self):
        """Test order total is calculated correctly"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='789 Elm St',
            town_or_city='Wiesbaden',
            postcode='65183',
            country='DE'
        )
        
        # Add line item
        OrderLineItem.objects.create(
            order=order,
            product=self.product,
            quantity=2
        )
        
        # Check totals
        self.assertEqual(order.order_total, Decimal('1999.98'))
        self.assertGreater(order.grand_total, order.order_total)
    
    def test_order_free_delivery_threshold(self):
        """Test free delivery over €50"""
        order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='789 Elm St',
            town_or_city='Wiesbaden',
            postcode='65183',
            country='DE'
        )
        
        # Add expensive item (over €50)
        OrderLineItem.objects.create(
            order=order,
            product=self.product,
            quantity=1
        )
        
        # Delivery should be free
        self.assertEqual(order.delivery_cost, Decimal('0'))


class OrderLineItemModelTest(TestCase):
    """Test OrderLineItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='accessories',
            friendly_name='Accessories'
        )
        self.product = Product.objects.create(
            name='Bike Helmet',
            price=Decimal('49.99'),
            category=self.category,
            stock_quantity=50,
            in_stock=True
        )
        self.order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            street_address1='123 Test St',
            town_or_city='Wiesbaden',
            postcode='65183',
            country='DE'
        )
    
    def test_lineitem_creation(self):
        """Test creating an order line item"""
        lineitem = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        self.assertEqual(lineitem.quantity, 2)
        self.assertEqual(lineitem.lineitem_total, Decimal('99.98'))
    
    def test_lineitem_total_calculation(self):
        """Test line item total is calculated correctly"""
        lineitem = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3
        )
        expected_total = self.product.price * 3
        self.assertEqual(lineitem.lineitem_total, expected_total)
