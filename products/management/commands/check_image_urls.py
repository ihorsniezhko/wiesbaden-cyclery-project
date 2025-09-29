"""
Management command to check product image URLs
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Check product image URLs'

    def handle(self, *args, **options):
        products = Product.objects.filter(pk__in=[301, 204, 408, 411, 505])[:5]
        
        for product in products:
            self.stdout.write(f'Product {product.pk}: {product.name}')
            self.stdout.write(f'  Image URL: {product.image_url}')
            self.stdout.write(f'  Image Field: {product.image}')
            self.stdout.write('---')