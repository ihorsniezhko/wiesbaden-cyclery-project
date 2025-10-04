#!/usr/bin/env python
"""
Debug script to test cart functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiesbaden_cyclery.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from shopping_cart.views import cart_view
from shopping_cart.utils import get_or_create_cart

def test_cart_functionality():
    """Test cart functionality step by step"""
    print("Testing cart functionality...")
    
    # Test 1: Test get_or_create_cart function
    print("\n1. Testing get_or_create_cart function...")
    try:
        factory = RequestFactory()
        request = factory.get('/cart/')
        request.user = AnonymousUser()
        
        # Create a proper session mock
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session.create()
        request.session = session
        
        cart = get_or_create_cart(request)
        print(f"✓ get_or_create_cart works: {cart}")
        
    except Exception as e:
        print(f"✗ get_or_create_cart failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Test cart view
    print("\n2. Testing cart view...")
    try:
        response = cart_view(request)
        print(f"✓ cart_view works: status {response.status_code}")
        
    except Exception as e:
        print(f"✗ cart_view failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_cart_functionality()