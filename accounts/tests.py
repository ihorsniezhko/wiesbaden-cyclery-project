"""
Tests for accounts app
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import UserProfile
from .forms import UserProfileForm


class UserProfileModelTestCase(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created automatically when User is created"""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertIsInstance(self.user.userprofile, UserProfile)
    
    def test_user_profile_str_method(self):
        """Test UserProfile string representation"""
        self.assertEqual(str(self.user.userprofile), 'testuser')
    
    def test_get_full_name_method(self):
        """Test get_full_name method"""
        profile = self.user.userprofile
        profile.first_name = 'John'
        profile.last_name = 'Doe'
        profile.save()
        
        self.assertEqual(profile.get_full_name(), 'John Doe')
    
    def test_get_full_name_empty(self):
        """Test get_full_name with empty names"""
        profile = self.user.userprofile
        self.assertEqual(profile.get_full_name(), '')


class BasicUserWorkflowTestCase(TestCase):
    """Test cases for basic user authentication workflows"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')
    
    def test_signup_page_loads(self):
        """Test that signup page loads successfully"""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
    
    def test_profile_requires_login(self):
        """Test that profile page requires authentication"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_page_authenticated(self):
        """Test profile page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Profile')
    
    def test_navigation_authenticated(self):
        """Test navigation shows correct links for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Sign Out')
    
    def test_navigation_anonymous(self):
        """Test navigation shows correct links for anonymous user"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Sign In')
        self.assertContains(response, 'Sign Up')


class ProfileFormTestCase(TestCase):
    """Test cases for UserProfile form"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.userprofile
    
    def test_profile_form_valid_data(self):
        """Test profile form with valid data"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'default_phone_number': '+49123456789',
            'default_street_address1': 'Test Street 123',
            'default_town_or_city': 'Wiesbaden',
            'default_postcode': '65189',
            'default_country': 'DE'
        }
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_profile_form_save(self):
        """Test that profile form saves correctly"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'default_phone_number': '+49123456789',
            'default_town_or_city': 'Wiesbaden',
        }
        form = UserProfileForm(data=form_data, instance=self.profile)
        if form.is_valid():
            form.save()
            
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'John')
        self.assertEqual(self.profile.last_name, 'Doe')
        self.assertEqual(self.profile.default_town_or_city, 'Wiesbaden')


class UserProfileAdminTestCase(TestCase):
    """Test cases for UserProfile admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
    
    def test_admin_can_access_userprofile(self):
        """Test that admin can access UserProfile in admin interface"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/accounts/userprofile/')
        self.assertEqual(response.status_code, 200)
    
    def test_userprofile_in_admin_list(self):
        """Test that UserProfile appears in admin list"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/accounts/userprofile/')
        self.assertContains(response, 'testuser')