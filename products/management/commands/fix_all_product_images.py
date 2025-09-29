"""
Management command to fix ALL product images including older products
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Fix ALL product images including older products'

    def handle(self, *args, **options):
        self.stdout.write('Fixing ALL product images...')
        
        # S3 media folder base URL
        s3_base_url = "https://wiesbaden-cyclery-project.s3.amazonaws.com/media/"
        
        # Map ALL products to appropriate images
        # For older products (1-10), use appropriate category images
        image_mappings = {
            # Original products (1-10) - assign appropriate S3 images
            1: "endurance-cruiser.jpg",           # Trek Domane AL 2 (road bike)
            2: "aero-speed-demon.jpg",            # Specialized Allez (road bike)
            3: "enduro-beast.jpg",                # Giant Talon (mountain bike)
            4: "trail-master-pro.jpg",            # Trek Fuel EX 5 (mountain bike)
            5: "pro-racing-helmet.jpg",           # Bike Helmet
            6: "led-light-set.jpg",               # Bike Lights
            7: "cycling-gloves.jpg",              # Cycling Gloves
            8: "water-bottle-set.jpg",            # Water Bottle
            9: "frame-bag.jpg",                   # Bike Pump (closest match)
            10: "bike-lock-security.jpg",         # Bike Lock
            
            # New products (101-604) - already mapped
            101: "urban-e-commuter-pro.jpg",
            102: "mountain-e-explorer.jpg",
            103: "city-e-cruiser.jpg",
            104: "performance-e-road.jpg",
            105: "folding-e-compact.jpg",
            106: "cargo-e-hauler.jpg",
            107: "fat-tire-e-adventure.jpg",
            108: "vintage-e-classic.jpg",
            201: "trail-master-pro.jpg",
            202: "enduro-beast.jpg",
            203: "cross-country-racer.jpg",
            204: "all-mountain-explorer.jpg",
            205: "hardtail-climber.jpg",
            206: "downhill-destroyer.jpg",
            207: "trail-starter.jpg",
            208: "plus-size-adventurer.jpg",
            301: "aero-speed-demon.jpg",
            302: "endurance-cruiser.jpg",
            303: "gravel-adventure.jpg",
            304: "classic-steel-tourer.jpg",
            305: "time-trial-rocket.jpg",
            306: "urban-commuter.jpg",
            307: "cyclocross-racer.jpg",
            308: "entry-level-roadie.jpg",
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
            601: "trail-master-pro.jpg",
            602: "urban-e-commuter-pro.jpg",
            603: "pro-racing-helmet.jpg",
            604: "carbon-wheelset.jpg",
        }
        
        updated_count = 0
        missing_files = []
        
        for product in Product.objects.all():
            if product.pk in image_mappings:
                filename = image_mappings[product.pk]
                image_url = f"{s3_base_url}{filename}"
                product.image_url = image_url
                product.save()
                updated_count += 1
                self.stdout.write(f'✓ {product.pk}: {product.name} → {filename}')
            else:
                missing_files.append(f'{product.pk}: {product.name}')
                self.stdout.write(self.style.WARNING(f'⚠ No mapping for {product.pk}: {product.name}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_count} product image URLs!'))
        
        if missing_files:
            self.stdout.write('')
            self.stdout.write(f'⚠ Products without mappings: {len(missing_files)}')
            for item in missing_files:
                self.stdout.write(f'  - {item}')
        
        self.stdout.write('')
        self.stdout.write('🔗 All products now point to S3 media folder!')