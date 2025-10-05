#!/usr/bin/env python
"""
Simple test runner for Wiesbaden Cyclery project
Runs all tests and displays a summary
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def run_tests():
    """Run all tests and display summary"""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'wiesbaden_cyclery.settings'
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    print("\n" + "="*70)
    print("WIESBADEN CYCLERY - TEST SUITE")
    print("="*70 + "\n")
    
    # Run tests
    failures = test_runner.run_tests([
        'products.tests',
        'orders.tests',
        'shopping_cart.tests',
    ])
    
    print("\n" + "="*70)
    if failures:
        print(f"TESTS FAILED: {failures} test(s) failed")
        print("="*70 + "\n")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED!")
        print("="*70 + "\n")
        sys.exit(0)

if __name__ == '__main__':
    run_tests()
