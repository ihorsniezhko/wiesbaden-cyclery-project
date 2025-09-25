"""
Management command to update products with local images
"""
from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Product
import os


class Command(BaseCommand):
    help = 'Update products with local images'

    def handle(self, *args, **options):
        self.stdout.write('Updating product images...')
        
        # Image mappings: product SKU -> image filename
        image_mappings = {
            'RB001': 'road_bikes/trek_domane.jpg',
            'RB002': 'road_bikes/specialized_allez.jpg',
            'MB001': 'mountain_bikes/giant_talon.jpg',
            'MB002': 'mountain_bikes/trek_fuel_ex.jpg',
            'EB001': 'electric_bikes/bosch_ebike.jpg',
            'AC001': 'accessories/bike_helmet.jpg',
            'AC002': 'accessories/cycling_gloves.jpg',
            'AC003': 'accessories/bike_lock.jpg',
            'AC004': 'accessories/water_bottle.jpg',
            'AC005': 'accessories/bike_lights.jpg',
            'AC006': 'accessories/bike_pump.jpg',
        }
        
        media_root = 'media/products/'
        
        for sku, image_path in image_mappings.items():
            try:
                product = Product.objects.get(sku=sku)
                full_image_path = os.path.join(media_root, image_path)
                
                if os.path.exists(full_image_path):
                    with open(full_image_path, 'rb') as img_file:
                        product.image.save(
                            os.path.basename(image_path),
                            File(img_file),
                            save=True
                        )
                    self.stdout.write(f'Updated image for {product.name}: {image_path}')
                else:
                    self.stdout.write(f'Image not found: {full_image_path}')
                    
            except Product.DoesNotExist:
                self.stdout.write(f'Product with SKU {sku} not found')
            except Exception as e:
                self.stdout.write(f'Error updating {sku}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS('Successfully updated product images'))