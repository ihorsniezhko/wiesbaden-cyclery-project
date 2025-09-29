"""
Management command to assign existing Unsplash images to products
"""
from django.core.management.base import BaseCommand
from products.models import Product, Category
import os


class Command(BaseCommand):
    help = 'Assign existing Unsplash images to products based on categories'

    def handle(self, *args, **options):
        self.stdout.write('Assigning existing Unsplash images to products...')
        
        # Map existing images to products by category
        image_assignments = {
            # Electric Bikes (8 products) - 3 images available
            101: "electric_bikes/electric_bike_1.jpg",  # Urban E-Commuter Pro
            102: "electric_bikes/electric_bike_2.jpg",  # Mountain E-Explorer
            103: "electric_bikes/bosch_ebike.jpg",      # City E-Cruiser
            104: "electric_bikes/electric_bike_1.jpg",  # Performance E-Road (reuse)
            105: "electric_bikes/electric_bike_2.jpg",  # Folding E-Compact (reuse)
            106: "electric_bikes/bosch_ebike.jpg",      # Cargo E-Hauler (reuse)
            107: "electric_bikes/electric_bike_1.jpg",  # Fat Tire E-Adventure (reuse)
            108: "electric_bikes/electric_bike_2.jpg",  # Vintage E-Classic (reuse)
            
            # Mountain Bikes (8 products) - 3 images available
            201: "mountain_bikes/trek_fuel_ex.jpg",     # Trail Master Pro
            202: "mountain_bikes/giant_talon.jpg",      # Enduro Beast
            203: "mountain_bikes/mountain_bike_1.jpg",  # Cross Country Racer
            204: "mountain_bikes/trek_fuel_ex.jpg",     # All-Mountain Explorer (reuse)
            205: "mountain_bikes/giant_talon.jpg",      # Hardtail Climber (reuse)
            206: "mountain_bikes/mountain_bike_1.jpg",  # Downhill Destroyer (reuse)
            207: "mountain_bikes/trek_fuel_ex.jpg",     # Trail Starter (reuse)
            208: "mountain_bikes/giant_talon.jpg",      # Plus Size Adventurer (reuse)
            
            # Road Bikes (8 products) - 2 images available
            301: "road_bikes/specialized_allez.jpg",    # Aero Speed Demon
            302: "road_bikes/trek_domane.jpg",          # Endurance Cruiser
            303: "road_bikes/specialized_allez.jpg",    # Gravel Adventure (reuse)
            304: "road_bikes/trek_domane.jpg",          # Classic Steel Tourer (reuse)
            305: "road_bikes/specialized_allez.jpg",    # Time Trial Rocket (reuse)
            306: "road_bikes/trek_domane.jpg",          # Urban Commuter (reuse)
            307: "road_bikes/specialized_allez.jpg",    # Cyclocross Racer (reuse)
            308: "road_bikes/trek_domane.jpg",          # Entry Level Roadie (reuse)
            
            # Accessories (12 products) - 6 images available
            401: "accessories/bike_helmet.jpg",         # Pro Racing Helmet
            402: "accessories/cycling_gloves.jpg",      # Cycling Jersey Pro (closest match)
            403: "accessories/cycling_gloves.jpg",      # Padded Cycling Shorts (reuse)
            404: "accessories/bike_lights.jpg",         # LED Light Set
            405: "accessories/cycling_gloves.jpg",      # Cycling Gloves
            406: "accessories/bike_pump.jpg",           # Frame Bag (closest match)
            407: "accessories/water_bottle.jpg",        # Water Bottle Set
            408: "accessories/bike_pump.jpg",           # Bike Computer GPS (closest match)
            409: "accessories/cycling_gloves.jpg",      # Cycling Shoes (reuse)
            410: "accessories/bike_pump.jpg",           # Multi-Tool Kit (reuse)
            411: "accessories/bike_lock.jpg",           # Bike Lock Security
            412: "accessories/bike_helmet.jpg",         # Cycling Sunglasses (reuse)
            
            # Components (10 products) - 4 images available
            501: "components/bike_wheel.jpg",           # Carbon Wheelset
            502: "components/bike_grips.jpg",           # Hydraulic Disc Brakes (closest match)
            503: "components/bike_grips.jpg",           # Electronic Shifting System (reuse)
            504: "components/bike_grips.jpg",           # Suspension Fork (reuse)
            505: "components/bike_grips.jpg",           # Carbon Handlebars (reuse)
            506: "components/bike_chain.jpg",           # Power Meter Crankset (closest match)
            507: "components/bike_tire.jpg",            # Tubeless Tire Set
            508: "components/bike_chain.jpg",           # Chain and Cassette Kit
            509: "components/bike_grips.jpg",           # Pedal System Clipless (reuse)
            510: "components/bike_grips.jpg",           # Saddle Performance (reuse)
            
            # Sale Items (4 products) - reuse existing images
            601: "mountain_bikes/trek_fuel_ex.jpg",     # Trail Master Pro - SALE
            602: "electric_bikes/electric_bike_1.jpg",  # Urban E-Commuter - CLEARANCE
            603: "accessories/bike_helmet.jpg",         # Pro Racing Helmet - DISCOUNT
            604: "components/bike_wheel.jpg",           # Carbon Wheelset - SPECIAL OFFER
        }
        
        # Base URL for local media files (will be served by Django in development, S3 in production)
        media_base_url = "products/"
        
        updated_count = 0
        missing_files = []
        
        for product_id, image_path in image_assignments.items():
            try:
                product = Product.objects.get(pk=product_id)
                
                # Check if the image file exists locally
                full_path = f"media/products/{image_path}"
                if os.path.exists(full_path):
                    # Set the image field to the relative path from media/
                    product.image = f"{media_base_url}{image_path}"
                    product.save()
                    updated_count += 1
                    self.stdout.write(f'✓ {product.name}: {product.image}')
                else:
                    missing_files.append(full_path)
                    self.stdout.write(self.style.WARNING(f'⚠ Missing file: {full_path}'))
                    
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Product {product_id} not found'))
        
        self.stdout.write('')
        self.stdout.write(f'Updated {updated_count} products with existing Unsplash images')
        
        if missing_files:
            self.stdout.write(f'Missing {len(missing_files)} image files:')
            for file_path in missing_files:
                self.stdout.write(f'  - {file_path}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Image assignment complete!'))