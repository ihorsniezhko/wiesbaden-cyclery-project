#!/usr/bin/env python
"""
Basic Test Runner for Wiesbaden Cyclery
Runs essential tests for Stage 1 development
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'wiesbaden_cyclery.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # List of basic test modules to run for Stage 1
    basic_tests = [
        'wiesbaden_cyclery.tests',
    ]
    
    print("Running Basic Tests for Wiesbaden Cyclery - Stage 1")
    print("=" * 55)
    print("These tests cover fundamental functionality:")
    print("- Homepage loading and template rendering")
    print("- Navigation and basic content")
    print("- Static files and templates configuration")
    print("- Database connection and admin access")
    print()
    
    failures = test_runner.run_tests(basic_tests)
    
    if failures:
        print(f"\n{failures} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll Stage 1 tests passed! ✅")
        print("\nStage 1 Test Coverage:")
        print("- Homepage functionality: ✅")
        print("- Template rendering: ✅")
        print("- Static files configuration: ✅")
        print("- Database connectivity: ✅")
        print("- Admin interface access: ✅")
        print("\nReady for Stage 2 development!")
        sys.exit(0)