from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from decimal import Decimal
from products.models import Product, Category, Size
from .models import Cart, CartItem
from .utils import get_or_create_cart, add_to_cart, update_cart_item, remove_from_cart


class CartModelTest(TestCase):
    """Test cart model functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category and product
        self.category = Category.objects.create(
            name='test_bikes',
            friendly_name='Test Bikes'
        )
        
        self.product = Product.objects.create(
            name='Test Bike',
            description='A test bicycle',
            price=Decimal('299.99'),
            category=self.category,
            sku='TEST001'
        )
        
        # Create test sizes
        self.size_m = Size.objects.create(name='M', display_name='Medium')
        self.size_l = Size.objects.create(name='L', display_name='Large')
        self.product.sizes.add(self.size_m, self.size_l)

    def test_cart_creation_for_user(self):
        """Test cart creation for authenticated user"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)
        self.assertIsNone(cart.session_key)
        self.assertEqual(str(cart), f"Cart for {self.user.username}")

    def test_cart_creation_for_session(self):
        """Test cart creation for anonymous session"""
        session_key = 'test_session_key_123'
        cart = Cart.objects.create(session_key=session_key)
        self.assertIsNone(cart.user)
        self.assertEqual(cart.session_key, session_key)
        self.assertTrue(str(cart).startswith("Anonymous cart"))

    def test_empty_cart_totals(self):
        """Test cart totals when empty"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.subtotal, 0)
        self.assertEqual(cart.delivery_cost, Decimal('4.99'))
        self.assertEqual(cart.total, Decimal('4.99'))

    def test_cart_with_items_under_50(self):
        """Test cart totals with items under €50"""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            size=self.size_m,
            quantity=1
        )
        
        self.assertEqual(cart.total_items, 1)
        self.assertEqual(cart.subtotal, Decimal('299.99'))
        self.assertEqual(cart.delivery_cost, Decimal('0.00'))  # Free over €50
        self.assertEqual(cart.total, Decimal('299.99'))

    def test_cart_with_items_over_50(self):
        """Test free delivery over €50"""
        # Create a cheaper product
        cheap_product = Product.objects.create(
            name='Cheap Item',
            description='A cheap item',
            price=Decimal('30.00'),
            category=self.category,
            sku='CHEAP001'
        )
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=cheap_product,
            quantity=1
        )
        
        self.assertEqual(cart.subtotal, Decimal('30.00'))
        self.assertEqual(cart.delivery_cost, Decimal('4.99'))
        self.assertEqual(cart.total, Decimal('34.99'))

    def test_cart_clear(self):
        """Test clearing cart items"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            size=self.size_m,
            quantity=2
        )
        
        self.assertEqual(cart.total_items, 2)
        cart.clear()
        self.assertEqual(cart.total_items, 0)


class CartItemModelTest(TestCase):
    """Test cart item model functionality"""

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
            sku='TEST001'
        )
        
        self.size_m = Size.objects.create(name='M', display_name='Medium')
        self.product.sizes.add(self.size_m)
        
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_item_creation(self):
        """Test cart item creation"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            size=self.size_m,
            quantity=2
        )
        
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.size, self.size_m)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(str(cart_item), "2x Test Bike (Medium)")

    def test_cart_item_line_total(self):
        """Test cart item line total calculation"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            size=self.size_m,
            quantity=3
        )
        
        expected_total = Decimal('100.00') * 3
        self.assertEqual(cart_item.line_total, expected_total)

    def test_cart_item_without_size(self):
        """Test cart item for product without sizes"""
        # Create product without sizes
        product_no_size = Product.objects.create(
            name='Accessory',
            description='An accessory',
            price=Decimal('25.00'),
            category=self.category,
            sku='ACC001'
        )
        
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=product_no_size,
            quantity=1
        )
        
        self.assertIsNone(cart_item.size)
        self.assertEqual(str(cart_item), "1x Accessory")


class CartUtilsTest(TestCase):
    """Test cart utility functions"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
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
            sku='TEST001'
        )
        
        self.size_m = Size.objects.create(name='M', display_name='Medium')
        self.product.sizes.add(self.size_m)

    def get_request_with_session(self, user=None):
        """Helper to create request with session"""
        request = self.factory.get('/')
        if user:
            request.user = user
        else:
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        
        # Add session middleware
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        
        return request

    def test_get_or_create_cart_authenticated(self):
        """Test cart creation for authenticated user"""
        request = self.get_request_with_session(self.user)
        cart = get_or_create_cart(request)
        
        self.assertEqual(cart.user, self.user)
        self.assertIsNone(cart.session_key)

    def test_get_or_create_cart_anonymous(self):
        """Test cart creation for anonymous user"""
        request = self.get_request_with_session()
        cart = get_or_create_cart(request)
        
        self.assertIsNone(cart.user)
        self.assertIsNotNone(cart.session_key)

    def test_add_to_cart(self):
        """Test adding product to cart"""
        request = self.get_request_with_session(self.user)
        cart_item = add_to_cart(request, self.product, self.size_m, 2)
        
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.size, self.size_m)
        self.assertEqual(cart_item.quantity, 2)

    def test_add_existing_item_to_cart(self):
        """Test adding existing item increases quantity"""
        request = self.get_request_with_session(self.user)
        
        # Add item first time
        add_to_cart(request, self.product, self.size_m, 1)
        
        # Add same item again
        cart_item = add_to_cart(request, self.product, self.size_m, 2)
        
        self.assertEqual(cart_item.quantity, 3)  # 1 + 2

    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        request = self.get_request_with_session(self.user)
        
        # Add item first
        add_to_cart(request, self.product, self.size_m, 1)
        
        # Update quantity
        cart_item = update_cart_item(request, self.product, self.size_m, 5)
        
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_from_cart(self):
        """Test removing item from cart"""
        request = self.get_request_with_session(self.user)
        
        # Add item first
        add_to_cart(request, self.product, self.size_m, 1)
        
        # Remove item
        result = remove_from_cart(request, self.product, self.size_m)
        
        self.assertTrue(result)
        
        # Verify item is removed
        cart = get_or_create_cart(request)
        self.assertEqual(cart.total_items, 0)