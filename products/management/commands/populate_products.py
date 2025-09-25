"""
Management command to populate products with proper data
"""
from django.core.management.base import BaseCommand
from products.models import Product, Category, Size


class Command(BaseCommand):
    help = 'Populate products with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating products...')
        
        # Get categories
        road_bikes = Category.objects.get(name='road_bikes')
        mountain_bikes = Category.objects.get(name='mountain_bikes')
        electric_bikes = Category.objects.get(name='electric_bikes')
        accessories = Category.objects.get(name='accessories')
        
        # Get sizes
        size_s = Size.objects.get(name='S')
        size_m = Size.objects.get(name='M')
        size_l = Size.objects.get(name='L')
        size_xl = Size.objects.get(name='XL')
        
        # Create products
        products_data = [
            {
                'category': road_bikes,
                'sku': 'RB001',
                'name': 'Trek Domane AL 2',
                'description': 'The Trek Domane AL 2 is an endurance road bike that\'s perfect for riders who want to go the distance in comfort. With a lightweight aluminum frame, carbon fork, and endurance geometry, this bike is built for long rides on varied terrain.',
                'has_sizes': True,
                'price': '899.99',
                'rating': '4.5',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',
                'in_stock': True,
                'stock_quantity': 15,
                'wheel_size': '700c',
                'gear_system': 'Shimano Claris 16-speed',
                'bicycle_features': 'Aluminum frame, carbon fork, endurance geometry',
                'sizes': [size_m, size_l]
            },
            {
                'category': road_bikes,
                'sku': 'RB002',
                'name': 'Specialized Allez Elite',
                'description': 'The Specialized Allez Elite is a performance road bike designed for speed and efficiency. With a lightweight aluminum frame and aggressive geometry, this bike is perfect for competitive riders and enthusiasts.',
                'has_sizes': True,
                'price': '1299.99',
                'rating': '4.7',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 8,
                'wheel_size': '700c',
                'gear_system': 'Shimano 105 22-speed',
                'bicycle_features': 'Lightweight aluminum frame, aggressive geometry, performance-oriented',
                'sizes': [size_m, size_l]
            },
            {
                'category': mountain_bikes,
                'sku': 'MB001',
                'name': 'Giant Talon 1',
                'description': 'The Giant Talon 1 is a versatile mountain bike that\'s perfect for trail riding and off-road adventures. With a durable aluminum frame, front suspension, and reliable components, this bike can handle any terrain.',
                'has_sizes': True,
                'price': '649.99',
                'rating': '4.3',
                'image_url': 'https://images.unsplash.com/photo-1544191696-15693072b5a5?w=800',
                'in_stock': True,
                'stock_quantity': 12,
                'wheel_size': '29"',
                'gear_system': 'Shimano Altus 24-speed',
                'bicycle_features': 'Aluminum frame, front suspension, trail-ready geometry',
                'sizes': [size_m, size_l]
            },
            {
                'category': mountain_bikes,
                'sku': 'MB002',
                'name': 'Trek Fuel EX 5',
                'description': 'The Trek Fuel EX 5 is a full-suspension mountain bike designed for aggressive trail riding. With 130mm of travel front and rear, this bike can handle the most challenging terrain with confidence.',
                'has_sizes': True,
                'price': '2199.99',
                'rating': '4.8',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 5,
                'wheel_size': '29"',
                'gear_system': 'SRAM NX Eagle 12-speed',
                'bicycle_features': 'Full suspension, 130mm travel, aggressive trail geometry',
                'sizes': [size_m, size_l]
            },
            {
                'category': electric_bikes,
                'sku': 'EB001',
                'name': 'Bosch Performance E-Bike',
                'description': 'Experience the future of cycling with our Bosch Performance E-Bike. Featuring a powerful Bosch motor and long-lasting battery, this e-bike makes every ride effortless and enjoyable.',
                'has_sizes': True,
                'price': '3299.99',
                'rating': '4.6',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 7,
                'wheel_size': '28"',
                'gear_system': 'Shimano Deore 10-speed',
                'bicycle_features': 'Bosch Performance motor, 500Wh battery, integrated display',
                'sizes': [size_m, size_l]
            },
            {
                'category': accessories,
                'sku': 'AC001',
                'name': 'Premium Bike Helmet',
                'description': 'Stay safe on your rides with our premium bike helmet. Featuring advanced ventilation, lightweight construction, and superior protection, this helmet is essential for every cyclist.',
                'has_sizes': True,
                'price': '89.99',
                'rating': '4.2',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 25,
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'category': accessories,
                'sku': 'AC002',
                'name': 'Cycling Gloves',
                'description': 'Enhance your grip and comfort with our professional cycling gloves. Featuring padded palms, breathable materials, and secure fit, these gloves are perfect for long rides.',
                'has_sizes': True,
                'price': '29.99',
                'rating': '4.0',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 40,
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'category': accessories,
                'sku': 'AC003',
                'name': 'Bike Lock',
                'description': 'Secure your investment with our heavy-duty bike lock. Featuring hardened steel construction and weather-resistant coating, this lock provides maximum security for your bicycle.',
                'has_sizes': False,
                'price': '49.99',
                'rating': '4.1',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 30,
                'sizes': []
            },
            {
                'category': accessories,
                'sku': 'AC004',
                'name': 'Water Bottle',
                'description': 'Stay hydrated on your rides with our premium water bottle. Featuring leak-proof design, easy-squeeze construction, and BPA-free materials, this bottle is perfect for any cycling adventure.',
                'has_sizes': False,
                'price': '12.99',
                'rating': '3.9',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 50,
                'sizes': []
            },
            {
                'category': accessories,
                'sku': 'AC005',
                'name': 'Bike Lights Set',
                'description': 'Increase your visibility and safety with our LED bike lights set. Featuring bright front and rear lights, multiple flash modes, and easy installation, these lights are essential for night riding.',
                'has_sizes': False,
                'price': '34.99',
                'rating': '4.3',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 35,
                'sizes': []
            },
            {
                'category': accessories,
                'sku': 'AC006',
                'name': 'Bike Pump',
                'description': 'Keep your tires properly inflated with our portable bike pump. Featuring dual valve compatibility, pressure gauge, and compact design, this pump is perfect for home and travel use.',
                'has_sizes': False,
                'price': '24.99',
                'rating': '4.0',
                'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
                'in_stock': True,
                'stock_quantity': 20,
                'sizes': []
            }
        ]
        
        for product_data in products_data:
            sizes = product_data.pop('sizes')
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            
            if created:
                product.sizes.set(sizes)
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated products'))