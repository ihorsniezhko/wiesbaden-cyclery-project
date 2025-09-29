"""
Management command to verify which product images exist in S3
"""
from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    help = 'Verify which product images exist in S3 bucket'

    def handle(self, *args, **options):
        s3_base_url = "https://wiesbaden-cyclery-project.s3.amazonaws.com/media/"
        
        # All unique image filenames needed
        required_images = [
            "aero-speed-demon.jpg", "all-mountain-explorer.jpg", "bike-computer-gps.jpg",
            "bike-lock-security.jpg", "carbon-handlebars.jpg", "carbon-wheelset.jpg",
            "cargo-e-hauler.jpg", "chain-and-cassette-kit.jpg", "city-e-cruiser.jpg",
            "classic-steel-tourer.jpg", "cross-country-racer.jpg", "cycling-gloves.jpg",
            "cycling-jersey-pro.jpg", "cycling-shoes.jpg", "cycling-sunglasses.jpg",
            "cyclocross-racer.jpg", "downhill-destroyer.jpg", "electronic-shifting-system.jpg",
            "endurance-cruiser.jpg", "enduro-beast.jpg", "entry-level-roadie.jpg",
            "fat-tire-e-adventure.jpg", "folding-e-compact.jpg", "frame-bag.jpg",
            "gravel-adventure.jpg", "hardtail-climber.jpg", "hydraulic-disc-brakes.jpg",
            "led-light-set.jpg", "mountain-e-explorer.jpg", "multi-tool-kit.jpg",
            "padded-cycling-shorts.jpg", "pedal-system-clipless.jpg", "performance-e-road.jpg",
            "plus-size-adventurer.jpg", "power-meter-crankset.jpg", "pro-racing-helmet.jpg",
            "saddle-performance.jpg", "suspension-fork.jpg", "time-trial-rocket.jpg",
            "trail-master-pro.jpg", "trail-starter.jpg", "tubeless-tire-set.jpg",
            "urban-commuter.jpg", "urban-e-commuter-pro.jpg", "vintage-e-classic.jpg",
            "water-bottle-set.jpg"
        ]
        
        self.stdout.write('=' * 80)
        self.stdout.write('VERIFYING S3 PRODUCT IMAGES')
        self.stdout.write('=' * 80)
        self.stdout.write(f'S3 Base URL: {s3_base_url}')
        self.stdout.write(f'Total images to check: {len(required_images)}')
        self.stdout.write('')
        
        found_images = []
        missing_images = []
        
        for i, filename in enumerate(required_images, 1):
            url = f"{s3_base_url}{filename}"
            self.stdout.write(f'{i:2d}. Checking: {filename}', ending='')
            
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    found_images.append(filename)
                    self.stdout.write(self.style.SUCCESS(' ✓ FOUND'))
                else:
                    missing_images.append(filename)
                    self.stdout.write(self.style.ERROR(f' ✗ Missing (Status: {response.status_code})'))
            except requests.exceptions.RequestException as e:
                missing_images.append(filename)
                self.stdout.write(self.style.ERROR(f' ✗ Error: {str(e)[:50]}...'))
        
        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write('SUMMARY')
        self.stdout.write('=' * 80)
        self.stdout.write(f'Found: {len(found_images)} images')
        self.stdout.write(f'Missing: {len(missing_images)} images')
        
        if missing_images:
            self.stdout.write('')
            self.stdout.write('MISSING IMAGES:')
            self.stdout.write('-' * 20)
            for filename in missing_images:
                self.stdout.write(f'  - {filename}')
        
        if found_images:
            self.stdout.write('')
            self.stdout.write('FOUND IMAGES:')
            self.stdout.write('-' * 15)
            for filename in found_images:
                self.stdout.write(f'  ✓ {filename}')
        
        self.stdout.write('')
        if len(found_images) == len(required_images):
            self.stdout.write(self.style.SUCCESS('🎉 ALL IMAGES FOUND! Ready to update product URLs.'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  {len(missing_images)} images still need to be uploaded.'))
        
        self.stdout.write('=' * 80)