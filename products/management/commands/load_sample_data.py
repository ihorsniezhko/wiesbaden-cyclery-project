"""
Management command to load sample product data
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from products.models import Product, Category, Size


class Command(BaseCommand):
    help = 'Load sample product data for Wiesbaden Cyclery'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data for Wiesbaden Cyclery...')
        
        # Load categories first
        try:
            call_command('loaddata', 'categories', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Categories loaded'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error loading categories: {e}'))
        
        # Load sizes
        try:
            call_command('loaddata', 'sizes', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Sizes loaded'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error loading sizes: {e}'))
        
        # Create products programmatically to avoid timestamp issues
        self.create_sample_products()
        
        # Summary
        categories_count = Category.objects.count()
        sizes_count = Size.objects.count()
        products_count = Product.objects.count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
        self.stdout.write(f'Categories: {categories_count}')
        self.stdout.write(f'Sizes: {sizes_count}')
        self.stdout.write(f'Products: {products_count}')
        self.stdout.write('='*50)

    def create_sample_products(self):
        """Create sample products programmatically"""
        
        # Get categories
        road_bikes = Category.objects.get(name='road_bikes')
        mountain_bikes = Category.objects.get(name='mountain_bikes')

        electric_bikes = Category.objects.get(name='electric_bikes')
        accessories = Category.objects.get(name='accessories')

        
        # Sample products data
        products_data = [
            {
                'category': road_bikes,
                'sku': 'RB001',
                'name': 'Trek Domane AL 2',
                'description': 'The Trek Domane AL 2 is an endurance road bike that\'s perfect for riders who want to go the distance in comfort.',
                'price': 899.99,
                'rating': 4.5,
                'stock_quantity': 15,
                'frame_size': '56cm',
                'wheel_size': '700c',
                'gear_system': 'Shimano Claris 16-speed',
            },
            {
                'category': road_bikes,
                'sku': 'RB002',
                'name': 'Specialized Allez Elite',
                'description': 'The Allez Elite is a premium aluminum road bike that delivers race-ready performance at an accessible price.',
                'price': 1299.99,
                'rating': 4.7,
                'stock_quantity': 8,
                'frame_size': '54cm',
                'wheel_size': '700c',
                'gear_system': 'Shimano 105 22-speed',
            },
            {
                'category': mountain_bikes,
                'sku': 'MB001',
                'name': 'Trek Marlin 7',
                'description': 'The Trek Marlin 7 is a cross-country mountain bike that\'s ready to take you places.',
                'price': 829.99,
                'rating': 4.6,
                'stock_quantity': 10,
                'frame_size': '17.5"',
                'wheel_size': '29"',
                'gear_system': 'Shimano Deore 12-speed',
            },
            {
                'category': mountain_bikes,
                'sku': 'MB002',
                'name': 'Specialized Rockhopper Sport 29',
                'description': 'The Rockhopper Sport 29 is built to handle anything the trail throws at you.',
                'price': 699.99,
                'rating': 4.4,
                'stock_quantity': 14,
                'frame_size': '16"',
                'wheel_size': '29"',
                'gear_system': 'Shimano Tourney 21-speed',
            },

            {
                'category': electric_bikes,
                'sku': 'EB001',
                'name': 'Trek Verve+ 2',
                'description': 'The Trek Verve+ 2 is an electric hybrid bike that makes every ride more enjoyable.',
                'price': 2299.99,
                'rating': 4.8,
                'stock_quantity': 5,
                'frame_size': '17.5"',
                'wheel_size': '700c',
                'gear_system': 'Shimano Acera 9-speed',
            },
            {
                'category': accessories,
                'sku': 'AC001',
                'name': 'Giro Register MIPS Helmet',
                'description': 'The Giro Register MIPS helmet offers essential protection with MIPS technology.',
                'price': 59.99,
                'rating': 4.3,
                'stock_quantity': 25,
                'has_sizes': True,
            },

        ]
        
        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {created_count} products created'))