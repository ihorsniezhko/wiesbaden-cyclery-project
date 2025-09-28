#!/usr/bin/env python
"""
Create sample products for the Wiesbaden Cyclery project
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiesbaden_cyclery.settings')
django.setup()

from products.models import Product, Category, Size
from decimal import Decimal

def create_sample_products():
    """Create sample products with integer ratings"""
    
    # Get categories
    try:
        road_bikes = Category.objects.get(name='Road Bikes')
        mountain_bikes = Category.objects.get(name='Mountain Bikes')
        accessories = Category.objects.get(name='Accessories')
        
        print("✅ Categories found")
    except Category.DoesNotExist as e:
        print(f"❌ Category not found: {e}")
        return False
    
    # Clear existing products
    Product.objects.all().delete()
    print("🗑️  Cleared existing products")
    
    # Create products with integer ratings
    products_data = [
        {
            'category': road_bikes,
            'sku': 'RB001',
            'name': 'Trek Domane AL 2',
            'description': 'The Trek Domane AL 2 is an endurance road bike perfect for long rides on varied terrain.',
            'price': Decimal('899.99'),
            'rating': 5,
            'image': 'trek_domane.jpg',
            'in_stock': True,
            'stock_quantity': 15,
            'wheel_size': '700c',
            'gear_system': 'Shimano Claris 16-speed',
            'bicycle_features': 'Aluminum frame, carbon fork, endurance geometry'
        },
        {
            'category': road_bikes,
            'sku': 'RB002',
            'name': 'Specialized Allez Elite',
            'description': 'The Specialized Allez Elite is a performance road bike designed for speed and efficiency.',
            'price': Decimal('1299.99'),
            'rating': 5,
            'image': 'specialized_allez.jpg',
            'in_stock': True,
            'stock_quantity': 8,
            'wheel_size': '700c',
            'gear_system': 'Shimano 105 22-speed',
            'bicycle_features': 'Lightweight aluminum frame, aggressive geometry'
        },
        {
            'category': mountain_bikes,
            'sku': 'MB001',
            'name': 'Giant Talon 1',
            'description': 'The Giant Talon 1 is a versatile mountain bike perfect for trail riding and off-road adventures.',
            'price': Decimal('699.99'),
            'rating': 4,
            'image': 'giant_talon.jpg',
            'in_stock': True,
            'stock_quantity': 12,
            'wheel_size': '29"',
            'gear_system': 'Shimano Altus 24-speed',
            'bicycle_features': 'Aluminum frame, front suspension, trail-ready'
        },
        {
            'category': mountain_bikes,
            'sku': 'MB002',
            'name': 'Trek Fuel EX 5',
            'description': 'The Trek Fuel EX 5 is a full-suspension mountain bike built for aggressive trail riding.',
            'price': Decimal('2199.99'),
            'rating': 5,
            'image': 'trek_fuel_ex.jpg',
            'in_stock': True,
            'stock_quantity': 6,
            'wheel_size': '29"',
            'gear_system': 'Shimano Deore 12-speed',
            'bicycle_features': 'Full suspension, aggressive trail geometry'
        },
        {
            'category': accessories,
            'sku': 'AC001',
            'name': 'Professional Cycling Helmet',
            'description': 'Professional cycling helmet with advanced safety features and comfortable fit.',
            'price': Decimal('79.99'),
            'rating': 5,
            'image': 'bike_helmet.jpg',
            'in_stock': True,
            'stock_quantity': 25,
            'has_sizes': True
        },
        {
            'category': accessories,
            'sku': 'AC002',
            'name': 'LED Bike Lights Set',
            'description': 'High-visibility LED bike lights set for safe night riding.',
            'price': Decimal('39.99'),
            'rating': 4,
            'image': 'bike_lights.jpg',
            'in_stock': True,
            'stock_quantity': 30,
            'has_sizes': False
        },
        {
            'category': accessories,
            'sku': 'AC003',
            'name': 'Cycling Gloves',
            'description': 'Comfortable cycling gloves with excellent grip and padding.',
            'price': Decimal('24.99'),
            'rating': 4,
            'image': 'cycling_gloves.jpg',
            'in_stock': True,
            'stock_quantity': 40,
            'has_sizes': True
        }
    ]
    
    created_count = 0
    for product_data in products_data:
        try:
            product = Product.objects.create(**product_data)
            
            # Add sizes for products that have sizes
            if product.has_sizes:
                sizes = Size.objects.all()
                if sizes.exists():
                    product.sizes.set(sizes)
                    print(f"✅ Added sizes to {product.name}")
            
            created_count += 1
            print(f"✅ Created: {product.name}")
            
        except Exception as e:
            print(f"❌ Error creating product: {e}")
    
    print(f"\n🎉 Successfully created {created_count} products!")
    return True

if __name__ == '__main__':
    success = create_sample_products()
    sys.exit(0 if success else 1)