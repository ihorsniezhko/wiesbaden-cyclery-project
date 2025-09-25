from django.core.management.base import BaseCommand
from products.models import Product, Category, Size


class Command(BaseCommand):
    help = 'Populate the database with sample products'

    def handle(self, *args, **options):
        # Clear existing products
        Product.objects.all().delete()
        
        # Get categories
        road_bikes = Category.objects.get(name='road_bikes')
        mountain_bikes = Category.objects.get(name='mountain_bikes')
        electric_bikes = Category.objects.get(name='electric_bikes')
        bmx_bikes = Category.objects.get(name='bmx_bikes')
        accessories = Category.objects.get(name='accessories')
        
        # Get sizes
        sizes = list(Size.objects.all())
        
        products_data = [
            {
                'category': road_bikes,
                'sku': 'RB001',
                'name': 'Trek Domane AL 2',
                'description': 'The Trek Domane AL 2 is an endurance road bike that\'s perfect for riders who want to go the distance in comfort. With a lightweight aluminum frame, carbon fork, and endurance geometry, this bike is built for long rides on varied terrain.',
                'has_sizes': False,
                'price': 899.99,
                'rating': 4.5,
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',
                'in_stock': True,
                'stock_quantity': 15,
                'frame_size': '56cm',
                'wheel_size': '700c',
                'gear_system': 'Shimano Claris 16-speed',
                'bicycle_features': 'Aluminum frame, carbon fork, endurance geometry'
            },
            {
                'category': road_bikes,
                'sku': 'RB002',
                'name': 'Specialized Allez Elite',
                'description': 'The Specialized Allez Elite is a performance road bike designed for speed and efficiency. With a lightweight aluminum frame and aggressive geometry, this bike is perfect for competitive riders and enthusiasts.',
                'has_sizes': False,
                'price': 1299.99,
                'rating': 4.7,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 8,
                'frame_size': '54cm',
                'wheel_size': '700c',
                'gear_system': 'Shimano 105 22-speed',
                'bicycle_features': 'Lightweight aluminum frame, aggressive geometry, performance-oriented'
            },
            {
                'category': mountain_bikes,
                'sku': 'MB001',
                'name': 'Giant Talon 1',
                'description': 'The Giant Talon 1 is a versatile mountain bike that\'s perfect for trail riding and off-road adventures. With a durable aluminum frame, front suspension, and reliable components, this bike can handle any terrain.',
                'has_sizes': False,
                'price': 649.99,
                'rating': 4.3,
                'image_url': 'https://images.unsplash.com/photo-1544191696-15693072b5a5?w=800',
                'in_stock': True,
                'stock_quantity': 12,
                'frame_size': 'M',
                'wheel_size': '29"',
                'gear_system': 'Shimano Altus 24-speed',
                'bicycle_features': 'Aluminum frame, front suspension, trail-ready geometry'
            },
            {
                'category': mountain_bikes,
                'sku': 'MB002',
                'name': 'Trek Fuel EX 5',
                'description': 'The Trek Fuel EX 5 is a full-suspension mountain bike designed for aggressive trail riding. With 130mm of travel front and rear, this bike can handle the most challenging terrain with confidence.',
                'has_sizes': False,
                'price': 2199.99,
                'rating': 4.8,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 5,
                'frame_size': 'L',
                'wheel_size': '29"',
                'gear_system': 'SRAM NX Eagle 12-speed',
                'bicycle_features': 'Full suspension, 130mm travel, aggressive trail geometry'
            },
            {
                'category': electric_bikes,
                'sku': 'EB001',
                'name': 'Bosch Performance E-Bike',
                'description': 'Experience the future of cycling with our Bosch Performance E-Bike. Featuring a powerful Bosch motor and long-lasting battery, this e-bike makes every ride effortless and enjoyable.',
                'has_sizes': False,
                'price': 3299.99,
                'rating': 4.6,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 7,
                'frame_size': 'M',
                'wheel_size': '28"',
                'gear_system': 'Shimano Deore 10-speed',
                'bicycle_features': 'Bosch Performance motor, 500Wh battery, integrated display'
            },
            {
                'category': bmx_bikes,
                'sku': 'CB001',
                'name': 'Brompton Folding Bike',
                'description': 'The Brompton Folding Bike is the perfect urban companion. Compact, lightweight, and incredibly portable, this bike folds down to a small package that fits under your desk or in a closet.',
                'has_sizes': False,
                'price': 1899.99,
                'rating': 4.4,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 10,
                'frame_size': 'One Size',
                'wheel_size': '16"',
                'gear_system': '3-speed internal hub',
                'bicycle_features': 'Folding design, lightweight steel frame, compact storage'
            },
            {
                'category': accessories,
                'sku': 'AC001',
                'name': 'Premium Bike Helmet',
                'description': 'Stay safe on your rides with our premium bike helmet. Featuring advanced ventilation, lightweight construction, and superior protection, this helmet is essential for every cyclist.',
                'has_sizes': True,
                'price': 89.99,
                'rating': 4.2,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 25
            },
            {
                'category': accessories,
                'sku': 'AC002',
                'name': 'Cycling Gloves',
                'description': 'Enhance your grip and comfort with our professional cycling gloves. Featuring padded palms, breathable materials, and secure fit, these gloves are perfect for long rides.',
                'has_sizes': True,
                'price': 29.99,
                'rating': 4.0,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 40
            },
            {
                'category': accessories,
                'sku': 'AC003',
                'name': 'Bike Lock',
                'description': 'Secure your investment with our heavy-duty bike lock. Featuring hardened steel construction and weather-resistant coating, this lock provides maximum security for your bicycle.',
                'has_sizes': False,
                'price': 49.99,
                'rating': 4.1,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 30
            },
            {
                'category': accessories,
                'sku': 'AC004',
                'name': 'Water Bottle',
                'description': 'Stay hydrated on your rides with our premium water bottle. Featuring leak-proof design, easy-squeeze construction, and BPA-free materials, this bottle is perfect for any cycling adventure.',
                'has_sizes': False,
                'price': 12.99,
                'rating': 3.9,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 50
            },
            {
                'category': accessories,
                'sku': 'AC005',
                'name': 'Bike Lights Set',
                'description': 'Increase your visibility and safety with our LED bike lights set. Featuring bright front and rear lights, multiple flash modes, and easy installation, these lights are essential for night riding.',
                'has_sizes': False,
                'price': 34.99,
                'rating': 4.3,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 35
            },
            {
                'category': accessories,
                'sku': 'AC006',
                'name': 'Bike Pump',
                'description': 'Keep your tires properly inflated with our portable bike pump. Featuring dual valve compatibility, pressure gauge, and compact design, this pump is perfect for home and travel use.',
                'has_sizes': False,
                'price': 24.99,
                'rating': 4.0,
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 20
            }
        ]
        
        created_count = 0
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            
            # Add sizes to products that have sizes
            if product.has_sizes and sizes:
                product.sizes.set(sizes[:3])  # Add first 3 sizes
            
            created_count += 1
            self.stdout.write(f'Created product: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} products')
        )