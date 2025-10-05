"""
Tests for Product views
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from products.models import Product, Category


class ProductListViewTest(TestCase):
    """Test product listing view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(
            name='road_bikes',
            friendly_name='Road Bikes'
        )
        self.product1 = Product.objects.create(
            name='Bike A',
            price=Decimal('999.99'),
            category=self.category,
            stock_quantity=10,
            in_stock=True
        )
        self.product2 = Product.objects.create(
            name='Bike B',
            price=Decimal('1299.99'),
            category=self.category,
            stock_quantity=5,
            in_stock=True
        )
    
    def test_products_page_loads(self):
        """Test products page loads successfully"""
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/products.html')
    
    def test_products_page_shows_products(self):
        """Test products are displayed on page"""
        response = self.client.get(reverse('products'))
        self.assertContains(response, 'Bike A')
        self.assertContains(response, 'Bike B')
    
    def test_products_filter_by_category(self):
        """Test filtering products by category"""
        response = self.client.get(reverse('products') + '?category=road_bikes')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bike A')
    
    def test_products_search(self):
        """Test product search functionality"""
        response = self.client.get(reverse('products') + '?q=Bike A')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bike A')
        self.assertNotContains(response, 'Bike B')
    
    def test_products_sort_by_price(self):
        """Test sorting products by price"""
        response = self.client.get(reverse('products') + '?sort=price&direction=asc')
        self.assertEqual(response.status_code, 200)
        # Should show products in price order


class ProductDetailViewTest(TestCase):
    """Test product detail view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(
            name='mountain_bikes',
            friendly_name='Mountain Bikes'
        )
        self.product = Product.objects.create(
            name='Mountain Bike Pro',
            description='Professional mountain bike',
            price=Decimal('1499.99'),
            category=self.category,
            stock_quantity=8,
            in_stock=True,
            rating=5
        )
    
    def test_product_detail_page_loads(self):
        """Test product detail page loads successfully"""
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
    
    def test_product_detail_shows_info(self):
        """Test product detail page shows product information"""
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertContains(response, 'Mountain Bike Pro')
        self.assertContains(response, '1499.99')
        self.assertContains(response, 'Professional mountain bike')
    
    def test_product_detail_invalid_id(self):
        """Test product detail with invalid ID returns 404"""
        response = self.client.get(reverse('product_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)
