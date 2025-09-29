"""
Management command to test different S3 image paths
"""
from django.core.management.base import BaseCommand
from products.models import Product
import requests


class Command(BaseCommand):
    help = 'Test different S3 image paths to find where images are stored'

    def handle(self, *args, **options):
        # Test different possible S3 paths
        bucket_name = "wiesbaden-cyclery-project"
        test_filename = "urban-e-commuter-pro.jpg"  # Test with first product
        
        possible_paths = [
            f"https://{bucket_name}.s3.amazonaws.com/media/product_images/{test_filename}",
            f"https://{bucket_name}.s3.amazonaws.com/media/{test_filename}",
            f"https://{bucket_name}.s3.amazonaws.com/product_images/{test_filename}",
            f"https://{bucket_name}.s3.amazonaws.com/images/{test_filename}",
            f"https://{bucket_name}.s3.amazonaws.com/{test_filename}",
            f"https://{bucket_name}.s3.us-east-1.amazonaws.com/media/product_images/{test_filename}",
            f"https://{bucket_name}.s3.us-east-1.amazonaws.com/media/{test_filename}",
            f"https://{bucket_name}.s3.us-east-1.amazonaws.com/product_images/{test_filename}",
            f"https://{bucket_name}.s3.us-east-1.amazonaws.com/images/{test_filename}",
            f"https://{bucket_name}.s3.us-east-1.amazonaws.com/{test_filename}",
        ]
        
        self.stdout.write(f'Testing S3 paths for: {test_filename}')
        self.stdout.write('=' * 50)
        
        for i, url in enumerate(possible_paths, 1):
            self.stdout.write(f'{i}. Testing: {url}')
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'   ✓ FOUND! Status: {response.status_code}'))
                    self.stdout.write(f'   Content-Type: {response.headers.get("Content-Type", "Unknown")}')
                    self.stdout.write(f'   Content-Length: {response.headers.get("Content-Length", "Unknown")}')
                else:
                    self.stdout.write(self.style.ERROR(f'   ✗ Not found. Status: {response.status_code}'))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'   ✗ Error: {str(e)}'))
            
            self.stdout.write('')