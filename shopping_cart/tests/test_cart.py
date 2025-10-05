"""
Tests for Shopping Cart functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from products.models import Product, Category, Size
from shopping_cart.models import Cart, CartItem


class CartModelTest(TestCase):
    """Test Cart model"""
    
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
    
    def test_cart_creation(self):
        """Test creating a cart"""
        cart = Cart.objects.create(session_key='test_session_123')
        self.assertEqual(cart.session_key, 'test_session_123')
        self.assertEqual(cart.total_items, 0)
    
    def test_cart_add_item(self):
        """Test adding item to cart"""
        cart = Cart.objects.create(session_key='test_session_123')
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart_item.line_total, Decimal('1999.98'))
    
    def test_cart_subtotal_calculation(self):
        """Test cart subtotal calculation"""
        cart = Cart.objects.create(session_key='test_session_123')
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )
        self.assertEqual(cart.subtotal, Decimal('999.99'))
    
    def test_cart_delivery_cost(self):
        """Test delivery cost calculation"""
        cart = Cart.objects.create(session_key='test_session_123')
        
        # Add cheap item (under €50)
        cheap_product = Product.objects.create(
            name='Cheap Item',
            price=Decimal('25.00'),
            category=self.category,
            stock_quantity=10,
            in_stock=True
        )
        CartItem.objects.create(
            cart=cart,
            product=cheap_product,
            quantity=1
        )
        
        # Delivery should be charged
        self.assertEqual(cart.delivery_cost, Decimal('4.99'))
    
    def test_cart_free_delivery(self):
        """Test free delivery over €50"""
        cart = Cart.objects.create(session_key='test_session_123')
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1
        )
        
        # Delivery should be free (product is €999.99)
        self.assertEqual(cart.delivery_cost, Decimal('0'))


class CartViewTest(TestCase):
    """Test Cart views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(
            name='accessories',
            friendly_name='Accessories'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('49.99'),
            category=self.category,
            stock_quantity=10,
            in_stock=True
        )
    
    def test_cart_view_loads(self):
        """Test cart page loads successfully"""
        response = self.client.get(reverse('shopping_cart:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopping_cart/cart.html')
    
    def test_add_to_cart(self):
        """Test adding product to cart"""
        response = self.client.post(
            reverse('shopping_cart:add_to_cart', args=[self.product.id]),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after add
    
    def test_cart_displays_items(self):
        """Test cart displays added items"""
        # Add item to cart
        self.client.post(
            reverse('shopping_cart:add_to_cart', args=[self.product.id]),
            {'quantity': 1}
        )
        
        # Check cart page
        response = self.client.get(reverse('shopping_cart:cart'))
        self.assertContains(response, self.product.name)
