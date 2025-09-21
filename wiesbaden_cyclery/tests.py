"""
Tests for main Wiesbaden Cyclery application
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class HomepageTestCase(TestCase):
    """Test cases for the homepage functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_homepage_loads(self):
        """Test that homepage loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wiesbaden Cyclery')
        self.assertContains(response, 'Welcome to Wiesbaden Cyclery')
    
    def test_homepage_template(self):
        """Test that homepage uses correct template"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/index.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_homepage_content(self):
        """Test that homepage contains expected content"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Expert Service')
        self.assertContains(response, 'Fast Delivery')
        self.assertContains(response, 'Quality Guarantee')
        self.assertContains(response, 'Expert Advice')
    
    def test_navigation_links(self):
        """Test that navigation contains expected links"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Home')
        self.assertContains(response, 'Products')
        self.assertContains(response, 'Cart')
        self.assertContains(response, 'Sign In')
        self.assertContains(response, 'Sign Up')


class BasicProjectTestCase(TestCase):
    """Test cases for basic project functionality"""
    
    def test_admin_accessible(self):
        """Test that admin interface is accessible"""
        response = self.client.get('/admin/')
        # Should redirect to login, not 404
        self.assertEqual(response.status_code, 302)
    
    def test_static_files_configured(self):
        """Test that static files are properly configured"""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        self.assertTrue(hasattr(settings, 'STATICFILES_DIRS'))
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
    
    def test_templates_configured(self):
        """Test that templates are properly configured"""
        from django.conf import settings
        template_dirs = settings.TEMPLATES[0]['DIRS']
        self.assertTrue(len(template_dirs) > 0)
    
    def test_database_connection(self):
        """Test that database connection works"""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)