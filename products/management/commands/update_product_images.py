"""
Management command to update product image URLs to point to AWS S3 images
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Update product image URLs to point to AWS S3 uploaded images'

    def handle(self, *args, **options):
        self.stdout.write('Updating product image URLs...')
        
        # S3 bucket base URL - single product_images folder
        s3_base_url = "https://wiesbaden-cyclery-project.s3.amazonaws.com/product_images/"
        
        # Define image mappings for products
        image_mappings = {
            # Electric Bikes - try common image file names
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
            
            # Sale Items (use same images as original products)
            601: "trail-master-pro.jpg",  # Trail Master Pro - SALE
            602: "urban-e-commuter-pro.jpg",  # Urban E-Commuter - CLEARANCE
            603: "pro-racing-helmet.jpg",  # Pro Racing Helmet - DISCOUNT
            604: "carbon-wheelset.jpg",  # Carbon Wheelset - SPECIAL OFFER
        }
        
        updated_count = 0
        
        for product_id, image_filename in image_mappings.items():
            try:
                product = Product.objects.get(pk=product_id)
                image_url = f"{s3_base_url}{image_filename}"
                product.image_url = image_url
                product.save()
                updated_count += 1
                self.stdout.write(f'Updated {product.name}: {image_url}')
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Product {product_id} not found'))
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} product image URLs!')
        )