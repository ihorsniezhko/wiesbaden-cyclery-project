"""
Management command to add components and sale items products
"""
from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Product, Category, Size
import os


class Command(BaseCommand):
    help = 'Add components and sale items products'

    def handle(self, *args, **options):
        self.stdout.write('Adding components and sale items products...')
        
        # Get categories
        components = Category.objects.get(name='components')
        sale_items = Category.objects.get(name='sale_items')
        accessories = Category.objects.get(name='accessories')
        road_bikes = Category.objects.get(name='road_bikes')
        
        # Get sizes for sale items that need them
        size_s = Size.objects.get(name='S')
        size_m = Size.objects.get(name='M')
        size_l = Size.objects.get(name='L')
        size_xl = Size.objects.get(name='XL')
        
        # Components products (no sizes)
        components_data = [
            {
                'category': components,
                'sku': 'CP001',
                'name': 'Shimano Chain',
                'description': 'High-quality Shimano bicycle chain for smooth and reliable shifting. Compatible with 9-speed drivetrains. Durable construction for long-lasting performance.',
                'has_sizes': False,
                'price': '24.99',
                'rating': '4.6',
                'in_stock': True,
                'stock_quantity': 50,
                'gear_system': '9-speed compatible',
                'bicycle_features': 'Corrosion resistant, quick-link included',
                'image_path': 'components/bike_chain.jpg'
            },
            {
                'category': components,
                'sku': 'CP002',
                'name': 'Professional Bike Wheel',
                'description': 'Lightweight aluminum alloy wheel with precision bearings. Perfect for road and hybrid bikes. Includes quick-release mechanism for easy installation.',
                'has_sizes': False,
                'price': '89.99',
                'rating': '4.8',
                'in_stock': True,
                'stock_quantity': 25,
                'wheel_size': '700c',
                'bicycle_features': 'Aluminum alloy rim, sealed bearings, quick-release',
                'image_path': 'components/bike_wheel.jpg'
            },
            {
                'category': components,
                'sku': 'CP003',
                'name': 'Premium Bike Tire',
                'description': 'High-performance bicycle tire with excellent grip and puncture resistance. Suitable for road and urban cycling with enhanced durability.',
                'has_sizes': False,
                'price': '34.99',
                'rating': '4.4',
                'in_stock': True,
                'stock_quantity': 40,
                'wheel_size': '700x25c',
                'bicycle_features': 'Puncture resistant, reflective sidewall, folding bead',
                'image_path': 'components/bike_tire.jpg'
            },
            {
                'category': components,
                'sku': 'CP004',
                'name': 'Ergonomic Handlebar Grips',
                'description': 'Comfortable ergonomic handlebar grips with anti-slip surface. Reduces hand fatigue during long rides. Easy installation with lock-on design.',
                'has_sizes': False,
                'price': '19.99',
                'rating': '4.3',
                'in_stock': True,
                'stock_quantity': 60,
                'bicycle_features': 'Ergonomic design, anti-slip surface, lock-on system',
                'image_path': 'components/bike_grips.jpg'
            }
        ]
        
        # Sale items (mix of categories, some with sizes)
        sale_items_data = [
            {
                'category': sale_items,
                'sku': 'SALE001',
                'name': 'Discounted Road Bike Helmet',
                'description': 'Premium road bike helmet at a special price! Lightweight design with excellent ventilation. MIPS technology for enhanced protection. Limited time offer.',
                'has_sizes': True,
                'price': '59.99',  # Reduced from regular price
                'rating': '4.5',
                'in_stock': True,
                'stock_quantity': 15,
                'bicycle_features': 'MIPS technology, 18 vents, lightweight',
                'image_path': 'accessories/bike_helmet.jpg',
                'sizes': [size_m, size_l, size_xl]
            },
            {
                'category': sale_items,
                'sku': 'SALE002',
                'name': 'Clearance Cycling Gloves',
                'description': 'Professional cycling gloves on clearance! Padded palms and breathable fabric. Perfect for long rides. Available in limited sizes while stocks last.',
                'has_sizes': True,
                'price': '19.99',  # Reduced from regular price
                'rating': '4.2',
                'in_stock': True,
                'stock_quantity': 20,
                'bicycle_features': 'Padded palms, breathable mesh, reflective details',
                'image_path': 'accessories/cycling_gloves.jpg',
                'sizes': [size_s, size_m, size_l]
            },
            {
                'category': sale_items,
                'sku': 'SALE003',
                'name': 'Special Offer Bike Chain',
                'description': 'High-quality bike chain at an unbeatable price! Perfect for maintenance and upgrades. Professional grade with corrosion resistance. Limited stock available.',
                'has_sizes': False,
                'price': '16.99',  # Reduced from regular price
                'rating': '4.4',
                'in_stock': True,
                'stock_quantity': 30,
                'gear_system': '8-9 speed compatible',
                'bicycle_features': 'Corrosion resistant, precision engineered',
                'image_path': 'components/bike_chain.jpg'
            }
        ]
        
        # Create components products
        for product_data in components_data:
            image_path = product_data.pop('image_path')
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            
            if created:
                # Add image
                full_image_path = os.path.join('media/products', image_path)
                if os.path.exists(full_image_path):
                    with open(full_image_path, 'rb') as img_file:
                        product.image.save(
                            os.path.basename(image_path),
                            File(img_file),
                            save=True
                        )
                
                self.stdout.write(f'Created component: {product.name}')
            else:
                self.stdout.write(f'Component already exists: {product.name}')
        
        # Create sale items products
        for product_data in sale_items_data:
            image_path = product_data.pop('image_path')
            sizes = product_data.pop('sizes', [])
            
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            
            if created:
                # Add sizes if any
                if sizes:
                    product.sizes.set(sizes)
                
                # Add image
                full_image_path = os.path.join('media/products', image_path)
                if os.path.exists(full_image_path):
                    with open(full_image_path, 'rb') as img_file:
                        product.image.save(
                            os.path.basename(image_path),
                            File(img_file),
                            save=True
                        )
                
                self.stdout.write(f'Created sale item: {product.name}')
            else:
                self.stdout.write(f'Sale item already exists: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully added components and sale items products'))