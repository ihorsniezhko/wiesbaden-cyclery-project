"""
Management command to prepare existing images for S3 media folder upload
"""
from django.core.management.base import BaseCommand
import os
import shutil


class Command(BaseCommand):
    help = 'Prepare existing local images for S3 media folder upload'

    def handle(self, *args, **options):
        self.stdout.write('Preparing images for S3 media folder upload...')
        
        # Create output directory for prepared images
        output_dir = 'prepared_images_for_s3'
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        
        # Map existing local images to final S3 filenames
        image_mappings = {
            # Electric Bikes - 3 source images, 8 products
            "electric_bikes/electric_bike_1.jpg": [
                "urban-e-commuter-pro.jpg",      # Product 101
                "performance-e-road.jpg",        # Product 104
                "fat-tire-e-adventure.jpg"       # Product 107
            ],
            "electric_bikes/electric_bike_2.jpg": [
                "mountain-e-explorer.jpg",       # Product 102
                "folding-e-compact.jpg",         # Product 105
                "vintage-e-classic.jpg"          # Product 108
            ],
            "electric_bikes/bosch_ebike.jpg": [
                "city-e-cruiser.jpg",            # Product 103
                "cargo-e-hauler.jpg"             # Product 106
            ],
            
            # Mountain Bikes - 3 source images, 8 products
            "mountain_bikes/trek_fuel_ex.jpg": [
                "trail-master-pro.jpg",          # Product 201
                "all-mountain-explorer.jpg",     # Product 204
                "trail-starter.jpg"              # Product 207
            ],
            "mountain_bikes/giant_talon.jpg": [
                "enduro-beast.jpg",              # Product 202
                "hardtail-climber.jpg",          # Product 205
                "plus-size-adventurer.jpg"       # Product 208
            ],
            "mountain_bikes/mountain_bike_1.jpg": [
                "cross-country-racer.jpg",       # Product 203
                "downhill-destroyer.jpg"         # Product 206
            ],
            
            # Road Bikes - 2 source images, 8 products
            "road_bikes/specialized_allez.jpg": [
                "aero-speed-demon.jpg",          # Product 301
                "gravel-adventure.jpg",          # Product 303
                "time-trial-rocket.jpg",         # Product 305
                "cyclocross-racer.jpg"           # Product 307
            ],
            "road_bikes/trek_domane.jpg": [
                "endurance-cruiser.jpg",         # Product 302
                "classic-steel-tourer.jpg",      # Product 304
                "urban-commuter.jpg",            # Product 306
                "entry-level-roadie.jpg"         # Product 308
            ],
            
            # Accessories - 6 source images, 12 products
            "accessories/bike_helmet.jpg": [
                "pro-racing-helmet.jpg",         # Product 401
                "cycling-sunglasses.jpg"         # Product 412
            ],
            "accessories/cycling_gloves.jpg": [
                "cycling-jersey-pro.jpg",        # Product 402
                "padded-cycling-shorts.jpg",     # Product 403
                "cycling-gloves.jpg",            # Product 405
                "cycling-shoes.jpg"              # Product 409
            ],
            "accessories/bike_lights.jpg": [
                "led-light-set.jpg"              # Product 404
            ],
            "accessories/bike_pump.jpg": [
                "frame-bag.jpg",                 # Product 406
                "bike-computer-gps.jpg",         # Product 408
                "multi-tool-kit.jpg"             # Product 410
            ],
            "accessories/water_bottle.jpg": [
                "water-bottle-set.jpg"           # Product 407
            ],
            "accessories/bike_lock.jpg": [
                "bike-lock-security.jpg"         # Product 411
            ],
            
            # Components - 4 source images, 10 products
            "components/bike_wheel.jpg": [
                "carbon-wheelset.jpg"            # Product 501 & 604 (sale)
            ],
            "components/bike_grips.jpg": [
                "hydraulic-disc-brakes.jpg",     # Product 502
                "electronic-shifting-system.jpg", # Product 503
                "suspension-fork.jpg",           # Product 504
                "carbon-handlebars.jpg",         # Product 505
                "pedal-system-clipless.jpg",     # Product 509
                "saddle-performance.jpg"         # Product 510
            ],
            "components/bike_chain.jpg": [
                "power-meter-crankset.jpg",      # Product 506
                "chain-and-cassette-kit.jpg"     # Product 508
            ],
            "components/bike_tire.jpg": [
                "tubeless-tire-set.jpg"          # Product 507
            ]
        }
        
        copied_files = []
        missing_files = []
        
        for source_path, target_filenames in image_mappings.items():
            source_file = f"media/products/{source_path}"
            
            if os.path.exists(source_file):
                for target_filename in target_filenames:
                    target_path = os.path.join(output_dir, target_filename)
                    shutil.copy2(source_file, target_path)
                    copied_files.append(target_filename)
                    self.stdout.write(f'✓ {source_path} → {target_filename}')
            else:
                missing_files.append(source_file)
                self.stdout.write(self.style.WARNING(f'⚠ Missing: {source_file}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Prepared {len(copied_files)} images for S3 upload!'))
        self.stdout.write(f'📁 Output folder: {output_dir}/')
        
        if missing_files:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'⚠ Missing {len(missing_files)} source files:'))
            for file in missing_files:
                self.stdout.write(f'  - {file}')
        
        self.stdout.write('')
        self.stdout.write('📋 NEXT STEPS:')
        self.stdout.write('1. Upload ALL files from prepared_images_for_s3/ folder')
        self.stdout.write('2. Upload to S3 bucket: wiesbaden-cyclery-project')
        self.stdout.write('3. Upload to folder: media/ (root media folder)')
        self.stdout.write('4. Set public read permissions on all images')
        self.stdout.write('5. Run: python manage.py update_s3_media_urls')
        
        # List all files to upload
        self.stdout.write('')
        self.stdout.write(f'📄 FILES TO UPLOAD ({len(copied_files)} total):')
        for i, filename in enumerate(sorted(copied_files), 1):
            self.stdout.write(f'  {i:2d}. {filename}')