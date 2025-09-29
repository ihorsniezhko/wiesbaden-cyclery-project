"""
Management command to list all required product images for S3 upload
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'List all required product image filenames for S3 upload'

    def handle(self, *args, **options):
        # Image filename mappings for all 50 products
        image_mappings = {
            # Electric Bikes (8 products)
            101: "urban-e-commuter-pro.jpg",
            102: "mountain-e-explorer.jpg", 
            103: "city-e-cruiser.jpg",
            104: "performance-e-road.jpg",
            105: "folding-e-compact.jpg",
            106: "cargo-e-hauler.jpg",
            107: "fat-tire-e-adventure.jpg",
            108: "vintage-e-classic.jpg",
            
            # Mountain Bikes (8 products)
            201: "trail-master-pro.jpg",
            202: "enduro-beast.jpg",
            203: "cross-country-racer.jpg", 
            204: "all-mountain-explorer.jpg",
            205: "hardtail-climber.jpg",
            206: "downhill-destroyer.jpg",
            207: "trail-starter.jpg",
            208: "plus-size-adventurer.jpg",
            
            # Road Bikes (8 products)
            301: "aero-speed-demon.jpg",
            302: "endurance-cruiser.jpg",
            303: "gravel-adventure.jpg",
            304: "classic-steel-tourer.jpg", 
            305: "time-trial-rocket.jpg",
            306: "urban-commuter.jpg",
            307: "cyclocross-racer.jpg",
            308: "entry-level-roadie.jpg",
            
            # Accessories (12 products)
            401: "pro-racing-helmet.jpg",
            402: "cycling-jersey-pro.jpg",
            403: "padded-cycling-shorts.jpg",
            404: "led-light-set.jpg",
            405: "cycling-gloves.jpg",
            406: "frame-bag.jpg",
            407: "water-bottle-set.jpg",
            408: "bike-computer-gps.jpg",
            409: "cycling-shoes.jpg",
            410: "multi-tool-kit.jpg",
            411: "bike-lock-security.jpg",
            412: "cycling-sunglasses.jpg",
            
            # Components (10 products)
            501: "carbon-wheelset.jpg",
            502: "hydraulic-disc-brakes.jpg",
            503: "electronic-shifting-system.jpg",
            504: "suspension-fork.jpg",
            505: "carbon-handlebars.jpg",
            506: "power-meter-crankset.jpg",
            507: "tubeless-tire-set.jpg",
            508: "chain-and-cassette-kit.jpg",
            509: "pedal-system-clipless.jpg",
            510: "saddle-performance.jpg",
            
            # Sale Items (4 products - reuse existing images)
            601: "trail-master-pro.jpg",  # Trail Master Pro - SALE
            602: "urban-e-commuter-pro.jpg",  # Urban E-Commuter - CLEARANCE
            603: "pro-racing-helmet.jpg",  # Pro Racing Helmet - DISCOUNT
            604: "carbon-wheelset.jpg",  # Carbon Wheelset - SPECIAL OFFER
        }
        
        self.stdout.write('=' * 80)
        self.stdout.write('REQUIRED PRODUCT IMAGES FOR S3 UPLOAD')
        self.stdout.write('=' * 80)
        self.stdout.write(f'S3 Bucket: wiesbaden-cyclery-project')
        self.stdout.write(f'Folder: product_images/')
        self.stdout.write(f'Total Products: {len(image_mappings)}')
        self.stdout.write('')
        
        # Get unique filenames (some sale items reuse images)
        unique_images = set(image_mappings.values())
        self.stdout.write(f'Unique Images Needed: {len(unique_images)}')
        self.stdout.write('')
        
        # List by category
        categories = {
            'Electric Bikes': range(101, 109),
            'Mountain Bikes': range(201, 209), 
            'Road Bikes': range(301, 309),
            'Accessories': range(401, 413),
            'Components': range(501, 511),
            'Sale Items': range(601, 605)
        }
        
        for category, id_range in categories.items():
            self.stdout.write(f'\n{category}:')
            self.stdout.write('-' * len(category))
            for product_id in id_range:
                if product_id in image_mappings:
                    try:
                        product = Product.objects.get(pk=product_id)
                        filename = image_mappings[product_id]
                        self.stdout.write(f'  {product_id:3d}: {filename:35s} ({product.name})')
                    except Product.DoesNotExist:
                        self.stdout.write(f'  {product_id:3d}: {image_mappings[product_id]:35s} (Product not found)')
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('UPLOAD INSTRUCTIONS:')
        self.stdout.write('=' * 80)
        self.stdout.write('1. Upload all images to S3 bucket: wiesbaden-cyclery-project')
        self.stdout.write('2. Create folder: product_images/')
        self.stdout.write('3. Upload images with exact filenames listed above')
        self.stdout.write('4. Set public read permissions on all images')
        self.stdout.write('5. Run: python manage.py update_product_images')
        self.stdout.write('')
        
        # List unique filenames for easy reference
        self.stdout.write('UNIQUE FILENAMES TO UPLOAD:')
        self.stdout.write('-' * 30)
        for i, filename in enumerate(sorted(unique_images), 1):
            self.stdout.write(f'{i:2d}. {filename}')
        
        self.stdout.write(f'\nTotal unique files to upload: {len(unique_images)}')
        self.stdout.write('=' * 80)