"""
Management command to check for products with missing images
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Check for products with missing images'

    def handle(self, *args, **options):
        self.stdout.write('Checking for products with missing images...')
        
        products_without_images = []
        products_with_images = []
        
        for product in Product.objects.all():
            if not product.image and not product.image_url:
                products_without_images.append(product)
            else:
                products_with_images.append(product)
        
        self.stdout.write('')
        self.stdout.write(f'✅ Products WITH images: {len(products_with_images)}')
        self.stdout.write(f'❌ Products WITHOUT images: {len(products_without_images)}')
        
        if products_without_images:
            self.stdout.write('')
            self.stdout.write('PRODUCTS WITHOUT IMAGES:')
            self.stdout.write('-' * 40)
            for product in products_without_images:
                self.stdout.write(f'  {product.pk}: {product.name}')
        
        # Also check for products with "Bosch", "Performance", "Clearance", or "Cycling Gloves"
        search_terms = ['Bosch', 'Performance', 'Clearance', 'Cycling Gloves']
        self.stdout.write('')
        self.stdout.write('PRODUCTS MATCHING YOUR SEARCH TERMS:')
        self.stdout.write('-' * 40)
        
        found_any = False
        for product in Product.objects.all():
            for term in search_terms:
                if term.lower() in product.name.lower():
                    found_any = True
                    has_image = "✅" if (product.image or product.image_url) else "❌"
                    self.stdout.write(f'  {has_image} {product.pk}: {product.name}')
                    if product.image_url:
                        self.stdout.write(f'      Image URL: {product.image_url}')
                    break
        
        if not found_any:
            self.stdout.write('  No products found with those terms.')
            self.stdout.write('')
            self.stdout.write('ALL PRODUCTS:')
            self.stdout.write('-' * 15)
            for product in Product.objects.all()[:20]:  # Show first 20
                has_image = "✅" if (product.image or product.image_url) else "❌"
                self.stdout.write(f'  {has_image} {product.pk}: {product.name}')