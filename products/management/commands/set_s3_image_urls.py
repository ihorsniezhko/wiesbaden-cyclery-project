"""
Management command to set S3 image URLs for products using existing image mapping
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Set S3 image URLs for products (assumes images are already uploaded to S3)'

    def handle(self, *args, **options):
        self.stdout.write('Setting S3 image URLs for products...')
        
        # S3 base URL
        s3_base_url = "https://wiesbaden-cyclery-project.s3.amazonaws.com/product_images/"
        
        # Map products to S3 filenames (using existing Unsplash images)
        image_mappings = {
            # Electric Bikes - using 3 different images rotated
            101: "urban-e-commuter-pro.jpg",      # electric_bike_1.jpg
            102: "mountain-e-explorer.jpg",       # electric_bike_2.jpg  
            103: "city-e-cruiser.jpg",            # bosch_ebike.jpg
            104: "performance-e-road.jpg",        # electric_bike_1.jpg (reuse)
            105: "folding-e-compact.jpg",         # electric_bike_2.jpg (reuse)
            106: "cargo-e-hauler.jpg",            # bosch_ebike.jpg (reuse)
            107: "fat-tire-e-adventure.jpg",      # electric_bike_1.jpg (reuse)
            108: "vintage-e-classic.jpg",         # electric_bike_2.jpg (reuse)
            
            # Mountain Bikes - using 3 different images rotated
            201: "trail-master-pro.jpg",          # trek_fuel_ex.jpg
            202: "enduro-beast.jpg",              # giant_talon.jpg
            203: "cross-country-racer.jpg",       # mountain_bike_1.jpg
            204: "all-mountain-explorer.jpg",     # trek_fuel_ex.jpg (reuse)
            205: "hardtail-climber.jpg",          # giant_talon.jpg (reuse)
            206: "downhill-destroyer.jpg",        # mountain_bike_1.jpg (reuse)
            207: "trail-starter.jpg",             # trek_fuel_ex.jpg (reuse)
            208: "plus-size-adventurer.jpg",      # giant_talon.jpg (reuse)
            
            # Road Bikes - using 2 different images alternated
            301: "aero-speed-demon.jpg",          # specialized_allez.jpg
            302: "endurance-cruiser.jpg",         # trek_domane.jpg
            303: "gravel-adventure.jpg",          # specialized_allez.jpg (reuse)
            304: "classic-steel-tourer.jpg",      # trek_domane.jpg (reuse)
            305: "time-trial-rocket.jpg",         # specialized_allez.jpg (reuse)
            306: "urban-commuter.jpg",            # trek_domane.jpg (reuse)
            307: "cyclocross-racer.jpg",          # specialized_allez.jpg (reuse)
            308: "entry-level-roadie.jpg",        # trek_domane.jpg (reuse)
            
            # Accessories - using 6 different images
            401: "pro-racing-helmet.jpg",         # bike_helmet.jpg
            402: "cycling-jersey-pro.jpg",        # cycling_gloves.jpg (closest match)
            403: "padded-cycling-shorts.jpg",     # cycling_gloves.jpg (reuse)
            404: "led-light-set.jpg",             # bike_lights.jpg
            405: "cycling-gloves.jpg",            # cycling_gloves.jpg
            406: "frame-bag.jpg",                 # bike_pump.jpg (closest match)
            407: "water-bottle-set.jpg",          # water_bottle.jpg
            408: "bike-computer-gps.jpg",         # bike_pump.jpg (reuse)
            409: "cycling-shoes.jpg",             # cycling_gloves.jpg (reuse)
            410: "multi-tool-kit.jpg",            # bike_pump.jpg (reuse)
            411: "bike-lock-security.jpg",        # bike_lock.jpg
            412: "cycling-sunglasses.jpg",        # bike_helmet.jpg (reuse)
            
            # Components - using 4 different images
            501: "carbon-wheelset.jpg",           # bike_wheel.jpg
            502: "hydraulic-disc-brakes.jpg",     # bike_grips.jpg
            503: "electronic-shifting-system.jpg", # bike_grips.jpg (reuse)
            504: "suspension-fork.jpg",           # bike_grips.jpg (reuse)
            505: "carbon-handlebars.jpg",         # bike_grips.jpg (reuse)
            506: "power-meter-crankset.jpg",      # bike_chain.jpg
            507: "tubeless-tire-set.jpg",         # bike_tire.jpg
            508: "chain-and-cassette-kit.jpg",    # bike_chain.jpg (reuse)
            509: "pedal-system-clipless.jpg",     # bike_grips.jpg (reuse)
            510: "saddle-performance.jpg",        # bike_grips.jpg (reuse)
            
            # Sale Items - reuse existing mappings
            601: "trail-master-pro.jpg",          # Same as product 201
            602: "urban-e-commuter-pro.jpg",      # Same as product 101
            603: "pro-racing-helmet.jpg",         # Same as product 401
            604: "carbon-wheelset.jpg",           # Same as product 501
        }
        
        updated_count = 0
        
        for product_id, filename in image_mappings.items():
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
        self.stdout.write('📋 NEXT STEPS:')
        self.stdout.write('1. Upload these images to S3 bucket: wiesbaden-cyclery-project')
        self.stdout.write('2. Create folder: product_images/')
        self.stdout.write('3. Upload images with the filenames shown above')
        self.stdout.write('4. Set public read permissions on all images')
        
        # Show unique filenames needed
        unique_files = set(image_mappings.values())
        self.stdout.write('')
        self.stdout.write(f'📁 UNIQUE FILES TO UPLOAD ({len(unique_files)} total):')
        for i, filename in enumerate(sorted(unique_files), 1):
            self.stdout.write(f'  {i:2d}. {filename}')
        
        self.stdout.write('')
        self.stdout.write('🔗 All product URLs are now set to point to S3!')