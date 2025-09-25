"""
Tests for products app
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command

from .models import Product, Category, Size, Review


class ProductModelTestCase(TestCase):
    """Test cases for Product model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            category=self.category,
            sku='TEST001',
            stock_quantity=10
        )
    
    def test_product_creation(self):
        """Test product creation"""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, 99.99)
        self.assertTrue(self.product.in_stock)
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_product_rating_display(self):
        """Test product rating display method"""
        self.product.rating = 4
        self.product.save()
        rating_display = self.product.get_rating_display()
        self.assertIn('★', rating_display)
        self.assertIn('☆', rating_display)


class CategoryModelTestCase(TestCase):
    """Test cases for Category model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='road_bikes',
            friendly_name='Road Bikes'
        )
    
    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, 'road_bikes')
        self.assertEqual(self.category.friendly_name, 'Road Bikes')
        self.assertEqual(str(self.category), 'road_bikes')
    
    def test_get_friendly_name(self):
        """Test get_friendly_name method"""
        self.assertEqual(self.category.get_friendly_name(), 'Road Bikes')


class SizeModelTestCase(TestCase):
    """Test cases for Size model"""
    
    def setUp(self):
        """Set up test data"""
        self.size = Size.objects.create(
            name='M',
            display_name='Medium',
            sort_order=3
        )
    
    def test_size_creation(self):
        """Test size creation"""
        self.assertEqual(self.size.name, 'M')
        self.assertEqual(self.size.display_name, 'Medium')
        self.assertEqual(self.size.sort_order, 3)
        self.assertEqual(str(self.size), 'Medium')


class ProductViewsTestCase(TestCase):
    """Test cases for product views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            category=self.category,
            sku='TEST001',
            stock_quantity=10
        )
    
    def test_products_page_loads(self):
        """Test that products page loads successfully"""
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Products')
        self.assertContains(response, 'Test Product')
    
    def test_product_detail_page_loads(self):
        """Test that product detail page loads successfully"""
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Test description')
    
    def test_product_search(self):
        """Test product search functionality"""
        response = self.client.get(reverse('products') + '?q=Test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_product_category_filter(self):
        """Test product category filtering"""
        response = self.client.get(reverse('products') + '?category=test_category')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_product_sorting(self):
        """Test product sorting functionality"""
        # Create another product for sorting test
        Product.objects.create(
            name='Another Product',
            description='Another description',
            price=149.99,
            category=self.category,
            sku='TEST002',
            stock_quantity=5
        )
        
        response = self.client.get(reverse('products') + '?sort=price&direction=asc')
        self.assertEqual(response.status_code, 200)
        # Should contain both products
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Another Product')


class ReviewModelTestCase(TestCase):
    """Test cases for Review model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            category=self.category,
            sku='TEST001',
            stock_quantity=10
        )
    
    def test_review_creation(self):
        """Test review creation"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            title='Great product!',
            rating=5,
            comment='Really love this product.'
        )
        
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(str(review), 'Great product! - 5 stars')
    
    def test_review_rating_display(self):
        """Test review rating display method"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            title='Good product',
            rating=4,
            comment='Pretty good product.'
        )
        
        rating_display = review.get_rating_display()
        self.assertIn('★', rating_display)
        self.assertIn('☆', rating_display)


class LoadSampleDataTestCase(TestCase):
    """Test cases for load_sample_data management command"""
    
    def test_load_sample_data_command(self):
        """Test that load_sample_data command works"""
        # Run the command
        call_command('load_sample_data')
        
        # Check that data was loaded
        self.assertTrue(Category.objects.exists())
        self.assertTrue(Size.objects.exists())
        self.assertTrue(Product.objects.exists())
        
        # Check specific counts
        self.assertEqual(Category.objects.count(), 10)
        self.assertEqual(Size.objects.count(), 19)
        self.assertTrue(Product.objects.count() >= 8)


class ProductAdminTestCase(TestCase):
    """Test cases for Product admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            category=self.category,
            sku='TEST001',
            stock_quantity=10
        )
        self.client = Client()
    
    def test_admin_can_access_products(self):
        """Test that admin can access products in admin interface"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/products/product/')
        self.assertEqual(response.status_code, 200)
    
    def test_product_in_admin_list(self):
        """Test that product appears in admin list"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/products/product/')
        self.assertContains(response, 'Test Product')