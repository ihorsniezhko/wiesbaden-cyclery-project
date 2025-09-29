"""
Management command to load 50 diverse products into the database
"""
from django.core.management.base import BaseCommand
from products.models import Product, Category, Size


class Command(BaseCommand):
    help = 'Load 50 diverse products following all steering rules'

    def handle(self, *args, **options):
        self.stdout.write('Loading 50 products...')
        
        # Get categories
        try:
            electric_bikes = Category.objects.get(name='electric_bikes')
            mountain_bikes = Category.objects.get(name='mountain_bikes')
            road_bikes = Category.objects.get(name='road_bikes')
            accessories = Category.objects.get(name='accessories')
            components = Category.objects.get(name='components')
            sale_items = Category.objects.get(name='sale_items')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('Categories not found. Please load categories first.'))
            return

        # Get sizes
        try:
            size_s = Size.objects.get(name='S')
            size_m = Size.objects.get(name='M')
            size_l = Size.objects.get(name='L')
            size_xl = Size.objects.get(name='XL')
        except Size.DoesNotExist:
            self.stdout.write(self.style.ERROR('Sizes not found. Please load sizes first.'))
            return

        # Clear existing products with these IDs
        Product.objects.filter(pk__in=range(101, 605)).delete()

        # Electric Bikes (8 products)
        products_data = [
            # Electric Bikes
            {
                'pk': 101, 'name': 'Urban E-Commuter Pro', 'category': electric_bikes,
                'description': 'Modern electric bike perfect for city commuting with 50km range and integrated lights.',
                'price': '2299.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano 8-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 102, 'name': 'Mountain E-Explorer', 'category': electric_bikes,
                'description': 'Powerful electric mountain bike with robust motor assistance for challenging trails.',
                'price': '3199.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '29"', 'gear_system': 'Shimano Deore XT',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 103, 'name': 'City E-Cruiser', 'category': electric_bikes,
                'description': 'Comfortable electric cruiser bike with step-through frame design.',
                'price': '1899.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '26"', 'gear_system': 'Shimano Nexus 7-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 104, 'name': 'Performance E-Road', 'category': electric_bikes,
                'description': 'High-performance electric road bike for serious cyclists.',
                'price': '4299.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano Ultegra Di2',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 105, 'name': 'Folding E-Compact', 'category': electric_bikes,
                'description': 'Compact folding electric bike ideal for urban storage and transport.',
                'price': '1599.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '20"', 'gear_system': 'Single speed',
                'sizes': []
            },
            {
                'pk': 106, 'name': 'Cargo E-Hauler', 'category': electric_bikes,
                'description': 'Heavy-duty electric cargo bike for family transport and deliveries.',
                'price': '2799.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '24"/20"', 'gear_system': 'Shimano Alfine 8-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 107, 'name': 'Fat Tire E-Adventure', 'category': electric_bikes,
                'description': 'All-terrain electric fat bike for sand, snow, and rough terrain.',
                'price': '2599.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '26" x 4"', 'gear_system': 'Shimano 9-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 108, 'name': 'Vintage E-Classic', 'category': electric_bikes,
                'description': 'Retro-styled electric bike combining classic aesthetics with modern technology.',
                'price': '2099.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano 7-speed',
                'sizes': [size_m, size_l]
            },
            
            # Mountain Bikes (8 products)
            {
                'pk': 201, 'name': 'Trail Master Pro', 'category': mountain_bikes,
                'description': 'Professional mountain bike designed for serious trail riding.',
                'price': '2899.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '29"', 'gear_system': 'Shimano XT 12-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 202, 'name': 'Enduro Beast', 'category': mountain_bikes,
                'description': 'Heavy-duty enduro mountain bike built for aggressive downhill riding.',
                'price': '3499.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '27.5"', 'gear_system': 'SRAM GX Eagle 12-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 203, 'name': 'Cross Country Racer', 'category': mountain_bikes,
                'description': 'Lightweight cross-country mountain bike optimized for racing.',
                'price': '2199.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '29"', 'gear_system': 'Shimano SLX 11-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 204, 'name': 'All-Mountain Explorer', 'category': mountain_bikes,
                'description': 'Versatile all-mountain bike suitable for various trail conditions.',
                'price': '1899.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '27.5"', 'gear_system': 'Shimano Deore 10-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 205, 'name': 'Hardtail Climber', 'category': mountain_bikes,
                'description': 'Efficient hardtail mountain bike designed for climbing and technical trails.',
                'price': '1599.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '29"', 'gear_system': 'Shimano Deore 11-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 206, 'name': 'Downhill Destroyer', 'category': mountain_bikes,
                'description': 'Specialized downhill mountain bike for extreme descents.',
                'price': '4199.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '27.5"', 'gear_system': 'SRAM X01 Eagle 12-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 207, 'name': 'Trail Starter', 'category': mountain_bikes,
                'description': 'Entry-level mountain bike perfect for beginners exploring trail riding.',
                'price': '899.99', 'rating': 3, 'has_sizes': True, 'wheel_size': '27.5"', 'gear_system': 'Shimano Altus 9-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 208, 'name': 'Plus Size Adventurer', 'category': mountain_bikes,
                'description': 'Mountain bike with plus-size tires for enhanced traction and comfort.',
                'price': '1799.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '27.5+', 'gear_system': 'Shimano SLX 12-speed',
                'sizes': [size_m, size_l]
            },
            
            # Road Bikes (8 products)
            {
                'pk': 301, 'name': 'Aero Speed Demon', 'category': road_bikes,
                'description': 'Aerodynamic road bike designed for maximum speed and efficiency.',
                'price': '3899.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano Ultegra Di2',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 302, 'name': 'Endurance Cruiser', 'category': road_bikes,
                'description': 'Comfortable endurance road bike for long-distance touring.',
                'price': '2599.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano 105 11-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 303, 'name': 'Gravel Adventure', 'category': road_bikes,
                'description': 'Versatile gravel road bike for mixed-terrain adventures.',
                'price': '2199.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano GRX 11-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 304, 'name': 'Classic Steel Tourer', 'category': road_bikes,
                'description': 'Traditional steel frame touring bike built for reliability.',
                'price': '1799.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano Tiagra 10-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 305, 'name': 'Time Trial Rocket', 'category': road_bikes,
                'description': 'Specialized time trial bike for individual racing events.',
                'price': '4599.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano Dura-Ace Di2',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 306, 'name': 'Urban Commuter', 'category': road_bikes,
                'description': 'Practical road bike designed for daily city commuting.',
                'price': '1299.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano Sora 9-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 307, 'name': 'Cyclocross Racer', 'category': road_bikes,
                'description': 'Competitive cyclocross bike for off-road racing and training.',
                'price': '2899.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'SRAM Force 1x11',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 308, 'name': 'Entry Level Roadie', 'category': road_bikes,
                'description': 'Affordable entry-level road bike perfect for beginners.',
                'price': '899.99', 'rating': 3, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano Claris 8-speed',
                'sizes': [size_m, size_l]
            },
            
            # Accessories (12 products)
            {
                'pk': 401, 'name': 'Pro Racing Helmet', 'category': accessories,
                'description': 'Lightweight aerodynamic helmet with advanced ventilation system.',
                'price': '159.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '', 'gear_system': '',
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'pk': 402, 'name': 'Cycling Jersey Pro', 'category': accessories,
                'description': 'Professional cycling jersey with moisture-wicking fabric.',
                'price': '89.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '', 'gear_system': '',
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'pk': 403, 'name': 'Padded Cycling Shorts', 'category': accessories,
                'description': 'High-quality cycling shorts with premium chamois padding.',
                'price': '79.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '', 'gear_system': '',
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'pk': 404, 'name': 'LED Light Set', 'category': accessories,
                'description': 'Powerful LED front and rear light set for safe night riding.',
                'price': '49.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 405, 'name': 'Cycling Gloves', 'category': accessories,
                'description': 'Padded cycling gloves with gel inserts for comfort and grip.',
                'price': '29.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '', 'gear_system': '',
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'pk': 406, 'name': 'Frame Bag', 'category': accessories,
                'description': 'Aerodynamic frame bag for storing essentials during rides.',
                'price': '39.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 407, 'name': 'Water Bottle Set', 'category': accessories,
                'description': 'Insulated water bottles with matching cage set.',
                'price': '24.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 408, 'name': 'Bike Computer GPS', 'category': accessories,
                'description': 'Advanced GPS bike computer with navigation and performance tracking.',
                'price': '299.99', 'rating': 5, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 409, 'name': 'Cycling Shoes', 'category': accessories,
                'description': 'Professional cycling shoes with carbon sole and BOA closure system.',
                'price': '199.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '', 'gear_system': '',
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'pk': 410, 'name': 'Multi-Tool Kit', 'category': accessories,
                'description': 'Comprehensive multi-tool kit with 16 functions.',
                'price': '34.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 411, 'name': 'Bike Lock Security', 'category': accessories,
                'description': 'Heavy-duty U-lock with cable extension for maximum security.',
                'price': '69.99', 'rating': 5, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 412, 'name': 'Cycling Sunglasses', 'category': accessories,
                'description': 'Sport sunglasses with interchangeable lenses and UV protection.',
                'price': '89.99', 'rating': 4, 'has_sizes': True, 'wheel_size': '', 'gear_system': '',
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            
            # Components (10 products)
            {
                'pk': 501, 'name': 'Carbon Wheelset', 'category': components,
                'description': 'Lightweight carbon fiber wheelset for road bikes.',
                'price': '1299.99', 'rating': 5, 'has_sizes': False, 'wheel_size': '700c', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 502, 'name': 'Hydraulic Disc Brakes', 'category': components,
                'description': 'High-performance hydraulic disc brake set with excellent stopping power.',
                'price': '349.99', 'rating': 5, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 503, 'name': 'Electronic Shifting System', 'category': components,
                'description': 'Precision electronic shifting system with wireless connectivity.',
                'price': '1899.99', 'rating': 5, 'has_sizes': False, 'wheel_size': '', 'gear_system': 'Electronic 12-speed',
                'sizes': []
            },
            {
                'pk': 504, 'name': 'Suspension Fork', 'category': components,
                'description': 'Advanced suspension fork with adjustable compression and rebound damping.',
                'price': '799.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 505, 'name': 'Carbon Handlebars', 'category': components,
                'description': 'Lightweight carbon fiber handlebars with ergonomic shape.',
                'price': '199.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 506, 'name': 'Power Meter Crankset', 'category': components,
                'description': 'Precision power meter crankset for training and performance analysis.',
                'price': '899.99', 'rating': 5, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 507, 'name': 'Tubeless Tire Set', 'category': components,
                'description': 'High-performance tubeless tires with puncture protection.',
                'price': '129.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '700c', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 508, 'name': 'Chain and Cassette Kit', 'category': components,
                'description': 'Premium chain and cassette combination for smooth shifting performance.',
                'price': '179.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '11-speed',
                'sizes': []
            },
            {
                'pk': 509, 'name': 'Pedal System Clipless', 'category': components,
                'description': 'Professional clipless pedal system with adjustable release tension.',
                'price': '149.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            {
                'pk': 510, 'name': 'Saddle Performance', 'category': components,
                'description': 'Ergonomic performance saddle with pressure relief channel.',
                'price': '249.99', 'rating': 4, 'has_sizes': False, 'wheel_size': '', 'gear_system': '',
                'sizes': []
            },
            
            # Sale Items (4 products)
            {
                'pk': 601, 'name': 'Trail Master Pro - SALE', 'category': sale_items,
                'description': 'Professional mountain bike designed for serious trail riding. SPECIAL DISCOUNT!',
                'price': '2299.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '29"', 'gear_system': 'Shimano XT 12-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 602, 'name': 'Urban E-Commuter - CLEARANCE', 'category': sale_items,
                'description': 'Modern electric bike perfect for city commuting. End of season clearance pricing!',
                'price': '1899.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '700c', 'gear_system': 'Shimano 8-speed',
                'sizes': [size_m, size_l]
            },
            {
                'pk': 603, 'name': 'Pro Racing Helmet - DISCOUNT', 'category': sale_items,
                'description': 'Lightweight aerodynamic helmet with MIPS technology. Limited time discount offer!',
                'price': '119.99', 'rating': 5, 'has_sizes': True, 'wheel_size': '', 'gear_system': '',
                'sizes': [size_s, size_m, size_l, size_xl]
            },
            {
                'pk': 604, 'name': 'Carbon Wheelset - SPECIAL OFFER', 'category': sale_items,
                'description': 'Lightweight carbon fiber wheelset for road bikes. Special promotional pricing!',
                'price': '999.99', 'rating': 5, 'has_sizes': False, 'wheel_size': '700c', 'gear_system': '',
                'sizes': []
            },
        ]

        # Create products
        created_count = 0
        for product_data in products_data:
            sizes = product_data.pop('sizes', [])
            
            # Add stock fields
            product_data['stock_quantity'] = 10
            product_data['in_stock'] = True
            
            product, created = Product.objects.get_or_create(
                pk=product_data['pk'],
                defaults=product_data
            )
            
            if created:
                created_count += 1
                # Add sizes if product has sizes
                if sizes:
                    product.sizes.set(sizes)
                
                self.stdout.write(f'Created: {product.name}')
            else:
                self.stdout.write(f'Updated: {product.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {created_count} products following all steering rules!')
        )