#!/usr/bin/env python
"""
SEO Implementation Verification Script
Checks that all NOINDEX meta tags are properly implemented
"""

import os
import re
from pathlib import Path

# Define templates that should have NOINDEX
NOINDEX_TEMPLATES = {
    'templates/shopping_cart/cart.html': 'Shopping Cart',
    'templates/orders/checkout.html': 'Checkout',
    'templates/orders/order_confirmation.html': 'Order Confirmation',
    'templates/orders/order_tracking.html': 'Order Tracking',
    'templates/account/login.html': 'Login',
    'templates/account/signup.html': 'Signup',
    'templates/account/password_reset.html': 'Password Reset',
    'templates/account/password_reset_done.html': 'Password Reset Done',
    'templates/account/password_reset_from_key.html': 'Password Change',
}

# Define templates that should have INDEX (default)
INDEX_TEMPLATES = {
    'templates/home/index.html': 'Home Page',
    'templates/products/products.html': 'Product List',
    'templates/products/product_detail.html': 'Product Detail',
}

def check_noindex_tag(file_path):
    """Check if a template file contains the noindex meta tag"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for the noindex meta tag
            pattern = r'<meta\s+name=["\']robots["\']\s+content=["\']noindex,\s*follow["\']'
            return bool(re.search(pattern, content, re.IGNORECASE))
    except FileNotFoundError:
        return None

def check_index_tag(file_path):
    """Check if a template file does NOT contain noindex (should use default index)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Should NOT have noindex
            pattern = r'<meta\s+name=["\']robots["\']\s+content=["\']noindex'
            return not bool(re.search(pattern, content, re.IGNORECASE))
    except FileNotFoundError:
        return None

def main():
    print("=" * 80)
    print("SEO IMPLEMENTATION VERIFICATION")
    print("=" * 80)
    print()
    
    # Check NOINDEX templates
    print("📋 Checking NOINDEX Templates (Should NOT be indexed by search engines)")
    print("-" * 80)
    
    noindex_pass = 0
    noindex_fail = 0
    
    for template_path, page_name in NOINDEX_TEMPLATES.items():
        full_path = Path(template_path)
        has_noindex = check_noindex_tag(full_path)
        
        if has_noindex is None:
            print(f"❌ {page_name:30} - FILE NOT FOUND: {template_path}")
            noindex_fail += 1
        elif has_noindex:
            print(f"✅ {page_name:30} - NOINDEX tag present")
            noindex_pass += 1
        else:
            print(f"❌ {page_name:30} - NOINDEX tag MISSING")
            noindex_fail += 1
    
    print()
    print(f"NOINDEX Results: {noindex_pass} passed, {noindex_fail} failed")
    print()
    
    # Check INDEX templates
    print("📋 Checking INDEX Templates (SHOULD be indexed by search engines)")
    print("-" * 80)
    
    index_pass = 0
    index_fail = 0
    
    for template_path, page_name in INDEX_TEMPLATES.items():
        full_path = Path(template_path)
        should_index = check_index_tag(full_path)
        
        if should_index is None:
            print(f"⚠️  {page_name:30} - FILE NOT FOUND: {template_path}")
            index_fail += 1
        elif should_index:
            print(f"✅ {page_name:30} - Using default INDEX (correct)")
            index_pass += 1
        else:
            print(f"❌ {page_name:30} - Has NOINDEX (incorrect!)")
            index_fail += 1
    
    print()
    print(f"INDEX Results: {index_pass} passed, {index_fail} failed")
    print()
    
    # Check robots.txt
    print("📋 Checking robots.txt Configuration")
    print("-" * 80)
    
    robots_path = Path('templates/robots.txt')
    if robots_path.exists():
        with open(robots_path, 'r') as f:
            robots_content = f.read()
            
        checks = {
            'Disallow /admin/': 'Disallow: /admin/' in robots_content,
            'Disallow /accounts/': 'Disallow: /accounts/' in robots_content,
            'Disallow /cart/': 'Disallow: /cart/' in robots_content,
            'Disallow /orders/': 'Disallow: /orders/' in robots_content,
            'Allow /products/': 'Allow: /products/' in robots_content,
            'Allow /static/': 'Allow: /static/' in robots_content,
            'Allow /media/': 'Allow: /media/' in robots_content,
            'Sitemap reference': 'Sitemap:' in robots_content,
        }
        
        robots_pass = sum(checks.values())
        robots_fail = len(checks) - robots_pass
        
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
        
        print()
        print(f"robots.txt Results: {robots_pass} passed, {robots_fail} failed")
    else:
        print("❌ robots.txt file not found!")
        robots_pass = 0
        robots_fail = 1
    
    print()
    
    # Check sitemap configuration
    print("📋 Checking Sitemap Configuration")
    print("-" * 80)
    
    sitemap_path = Path('wiesbaden_cyclery/sitemaps.py')
    if sitemap_path.exists():
        with open(sitemap_path, 'r') as f:
            sitemap_content = f.read()
            
        checks = {
            'StaticViewSitemap class': 'class StaticViewSitemap' in sitemap_content,
            'ProductSitemap class': 'class ProductSitemap' in sitemap_content,
            'CategorySitemap class': 'class CategorySitemap' in sitemap_content,
            'Product filtering': 'in_stock=True' in sitemap_content,
        }
        
        sitemap_pass = sum(checks.values())
        sitemap_fail = len(checks) - sitemap_pass
        
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
        
        print()
        print(f"Sitemap Results: {sitemap_pass} passed, {sitemap_fail} failed")
    else:
        print("❌ sitemaps.py file not found!")
        sitemap_pass = 0
        sitemap_fail = 1
    
    print()
    print("=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    
    total_pass = noindex_pass + index_pass + robots_pass + sitemap_pass
    total_fail = noindex_fail + index_fail + robots_fail + sitemap_fail
    total_tests = total_pass + total_fail
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_pass} ✅")
    print(f"Failed: {total_fail} ❌")
    print(f"Success Rate: {(total_pass/total_tests*100):.1f}%")
    print()
    
    if total_fail == 0:
        print("🎉 ALL TESTS PASSED! SEO implementation is complete and correct.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    exit(main())
