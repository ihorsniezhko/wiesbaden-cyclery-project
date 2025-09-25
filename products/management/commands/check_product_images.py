"""
Management command to check product images
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Check product images'

    def handle(self, *args, **options):
        self.stdout.write('Checking product images...')
        
        for product in Product.objects.all():
            image_status = product.image.name if product.image else "No image"
            self.stdout.write(f'{product.sku}: {product.name} - Image: {image_status}')
        
        self.stdout.write(self.style.SUCCESS('Image check complete'))