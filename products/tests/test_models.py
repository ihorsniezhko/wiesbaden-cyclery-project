"""
Tests for Product models
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from products.models import Product, Category, Size


class CategoryModelTest(TestCase):
    """Test Category model"""
    
    def test_category_creation(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='road_bikes',
            friendly_name='Road Bikes'
        )
        self.assertEqual(category.name, 'road_bikes')
        self.assertEqual(category.friendly_name, 'Road Bikes')
        self.assertEqual(str(category), 'Road Bikes')  # __str__ returns friendly_name
    
    def test_category_get_friendly_name(self):
        """Test get_friendly_name method"""
        category = Category.objects.create(
            name='mountain_bikes',
            friendly_name='Mountain Bikes'
        )
        self.assertEqual(category.get_friendly_name(), 'Mountain Bikes')


class SizeModelTest(TestCase):
    """Test Size model"""
    
    def test_size_creation(self):
        """Test creating a size"""
        size = Size.objects.create(
            name='M',
            display_name='Medium',
            sort_order=2
        )
        self.assertEqual(size.name, 'M')
        self.assertEqual(size.display_name, 'Medium')
        self.assertEqual(str(size), 'Medium')
    
    def test_size_ordering(self):
        """Test sizes are ordered by sort_order"""
        Size.objects.create(name='L', display_name='Large', sort_order=3)
        Size.objects.create(name='S', display_name='Small', sort_order=1)
        Size.objects.create(name='M', display_name='Medium', sort_order=2)
        
        sizes = Size.objects.all()
        self.assertEqual(sizes[0].name, 'S')
        self.assertEqual(sizes[1].name, 'M')
        self.assertEqual(sizes[2].name, 'L')


class ProductModelTest(TestCase):
    """Test Product model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='road_bikes',
            friendly_name='Road Bikes'
        )
        self.size_m = Size.objects.create(
            name='M',
            display_name='Medium',
            sort_order=2
        )
        self.size_l = Size.objects.create(
            name='L',
            display_name='Large',
            sort_order=3
        )
    
    def test_product_creation(self):
        """Test creating a product"""
        product = Product.objects.create(
            name='Test Bike',
            description='A test bicycle',
            price=Decimal('999.99'),
            category=self.category,
            stock_quantity=10,
            in_stock=True,
            rating=5
        )
        self.assertEqual(product.name, 'Test Bike')
        self.assertEqual(product.price, Decimal('999.99'))
        self.assertTrue(product.in_stock)
        self.assertEqual(str(product), 'Test Bike')
    
    def test_product_with_sizes(self):
        """Test product with multiple sizes"""
        product = Product.objects.create(
            name='Sized Bike',
            price=Decimal('1299.99'),
            category=self.category,
            has_sizes=True,
            stock_quantity=20,
            in_stock=True
        )
        product.sizes.add(self.size_m, self.size_l)
        
        self.assertTrue(product.has_sizes)
        self.assertEqual(product.sizes.count(), 2)
        self.assertIn(self.size_m, product.sizes.all())
    
    def test_product_stock_validation(self):
        """Test stock quantity validation"""
        product = Product(
            name='Invalid Stock Bike',
            price=Decimal('999.99'),
            category=self.category,
            in_stock=True,
            stock_quantity=0  # Invalid: in_stock but no quantity
        )
        with self.assertRaises(ValidationError):
            product.full_clean()
    
    def test_product_rating_validation(self):
        """Test rating is within valid range"""
        product = Product.objects.create(
            name='Rated Bike',
            price=Decimal('999.99'),
            category=self.category,
            stock_quantity=10,
            in_stock=True,
            rating=5
        )
        self.assertGreaterEqual(product.rating, 1)
        self.assertLessEqual(product.rating, 5)
    
    def test_product_out_of_stock(self):
        """Test product marked as out of stock"""
        product = Product.objects.create(
            name='Out of Stock Bike',
            price=Decimal('999.99'),
            category=self.category,
            in_stock=False,
            stock_quantity=0
        )
        self.assertFalse(product.in_stock)
        self.assertEqual(product.stock_quantity, 0)
