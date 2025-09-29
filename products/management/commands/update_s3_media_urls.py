"""
Management command to update product image URLs to point to S3 media folder
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Update product image URLs to point to S3 media folder'

    def handle(self, *args, **options):
        self.stdout.write('Updating product image URLs to S3 media folder...')
        
        # S3 media folder base URL
        s3_base_url = "https://wiesbaden-cyclery-project.s3.amazonaws.com/media/"
        
        # Map products to their S3 media filenames
        product_image_mapping = {
            # Electric Bikes
            101: "urban-e-commuter-pro.jpg",
            102: "mountain-e-explorer.jpg",
            103: "city-e-cruiser.jpg",
            104: "performance-e-road.jpg",
            105: "folding-e-compact.jpg",
            106: "cargo-e-hauler.jpg",
            107: "fat-tire-e-adventure.jpg",
            108: "vintage-e-classic.jpg",
            
            # Mountain Bikes
            201: "trail-master-pro.jpg",
            202: "enduro-beast.jpg",
            203: "cross-country-racer.jpg",
            204: "all-mountain-explorer.jpg",
            205: "hardtail-climber.jpg",
            206: "downhill-destroyer.jpg",
            207: "trail-starter.jpg",
            208: "plus-size-adventurer.jpg",
            
            # Road Bikes
            301: "aero-speed-demon.jpg",
            302: "endurance-cruiser.jpg",
            303: "gravel-adventure.jpg",
            304: "classic-steel-tourer.jpg",
            305: "time-trial-rocket.jpg",
            306: "urban-commuter.jpg",
            307: "cyclocross-racer.jpg",
            308: "entry-level-roadie.jpg",
            
            # Accessories
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
            
            # Components
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
            
            # Sale Items (reuse existing filenames)
            601: "trail-master-pro.jpg",          # Same as 201
            602: "urban-e-commuter-pro.jpg",      # Same as 101
            603: "pro-racing-helmet.jpg",         # Same as 401
            604: "carbon-wheelset.jpg",           # Same as 501
        }
        
        updated_count = 0
        
        for product_id, filename in product_image_mapping.items():
            try:
                product = Product.objects.get(pk=product_id)
                image_url = f"{s3_base_url}{filename}"
                product.image_url = image_url
                product.save()
                updated_count += 1
                self.stdout.write(f'✓ {product.name}: {filename}')
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Product {product_id} not found'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_count} product image URLs!'))
        self.stdout.write('')
        self.stdout.write('🔗 All products now point to:')
        self.stdout.write(f'   {s3_base_url}[filename]')
        self.stdout.write('')
        self.stdout.write('📋 VERIFY UPLOAD:')
        self.stdout.write('Run: python manage.py verify_s3_images')
        
        # Show unique filenames for verification
        unique_files = set(product_image_mapping.values())
        self.stdout.write('')
        self.stdout.write(f'📄 EXPECTED FILES IN S3 MEDIA FOLDER ({len(unique_files)} total):')
        for i, filename in enumerate(sorted(unique_files), 1):
            self.stdout.write(f'  {i:2d}. {filename}')