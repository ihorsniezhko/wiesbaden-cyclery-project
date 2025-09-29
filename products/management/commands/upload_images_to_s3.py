"""
Management command to upload existing local images to S3 product_images folder
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product
import boto3
import os
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Upload existing local images to S3 product_images folder and update product URLs'

    def handle(self, *args, **options):
        self.stdout.write('Uploading local images to S3 product_images folder...')
        
        # AWS S3 configuration
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3_folder = 'product_images/'
        
        # Map existing local images to products
        image_assignments = {
            # Electric Bikes
            101: ("electric_bikes/electric_bike_1.jpg", "urban-e-commuter-pro.jpg"),
            102: ("electric_bikes/electric_bike_2.jpg", "mountain-e-explorer.jpg"),
            103: ("electric_bikes/bosch_ebike.jpg", "city-e-cruiser.jpg"),
            104: ("electric_bikes/electric_bike_1.jpg", "performance-e-road.jpg"),
            105: ("electric_bikes/electric_bike_2.jpg", "folding-e-compact.jpg"),
            106: ("electric_bikes/bosch_ebike.jpg", "cargo-e-hauler.jpg"),
            107: ("electric_bikes/electric_bike_1.jpg", "fat-tire-e-adventure.jpg"),
            108: ("electric_bikes/electric_bike_2.jpg", "vintage-e-classic.jpg"),
            
            # Mountain Bikes
            201: ("mountain_bikes/trek_fuel_ex.jpg", "trail-master-pro.jpg"),
            202: ("mountain_bikes/giant_talon.jpg", "enduro-beast.jpg"),
            203: ("mountain_bikes/mountain_bike_1.jpg", "cross-country-racer.jpg"),
            204: ("mountain_bikes/trek_fuel_ex.jpg", "all-mountain-explorer.jpg"),
            205: ("mountain_bikes/giant_talon.jpg", "hardtail-climber.jpg"),
            206: ("mountain_bikes/mountain_bike_1.jpg", "downhill-destroyer.jpg"),
            207: ("mountain_bikes/trek_fuel_ex.jpg", "trail-starter.jpg"),
            208: ("mountain_bikes/giant_talon.jpg", "plus-size-adventurer.jpg"),
            
            # Road Bikes
            301: ("road_bikes/specialized_allez.jpg", "aero-speed-demon.jpg"),
            302: ("road_bikes/trek_domane.jpg", "endurance-cruiser.jpg"),
            303: ("road_bikes/specialized_allez.jpg", "gravel-adventure.jpg"),
            304: ("road_bikes/trek_domane.jpg", "classic-steel-tourer.jpg"),
            305: ("road_bikes/specialized_allez.jpg", "time-trial-rocket.jpg"),
            306: ("road_bikes/trek_domane.jpg", "urban-commuter.jpg"),
            307: ("road_bikes/specialized_allez.jpg", "cyclocross-racer.jpg"),
            308: ("road_bikes/trek_domane.jpg", "entry-level-roadie.jpg"),
            
            # Accessories
            401: ("accessories/bike_helmet.jpg", "pro-racing-helmet.jpg"),
            402: ("accessories/cycling_gloves.jpg", "cycling-jersey-pro.jpg"),
            403: ("accessories/cycling_gloves.jpg", "padded-cycling-shorts.jpg"),
            404: ("accessories/bike_lights.jpg", "led-light-set.jpg"),
            405: ("accessories/cycling_gloves.jpg", "cycling-gloves.jpg"),
            406: ("accessories/bike_pump.jpg", "frame-bag.jpg"),
            407: ("accessories/water_bottle.jpg", "water-bottle-set.jpg"),
            408: ("accessories/bike_pump.jpg", "bike-computer-gps.jpg"),
            409: ("accessories/cycling_gloves.jpg", "cycling-shoes.jpg"),
            410: ("accessories/bike_pump.jpg", "multi-tool-kit.jpg"),
            411: ("accessories/bike_lock.jpg", "bike-lock-security.jpg"),
            412: ("accessories/bike_helmet.jpg", "cycling-sunglasses.jpg"),
            
            # Components
            501: ("components/bike_wheel.jpg", "carbon-wheelset.jpg"),
            502: ("components/bike_grips.jpg", "hydraulic-disc-brakes.jpg"),
            503: ("components/bike_grips.jpg", "electronic-shifting-system.jpg"),
            504: ("components/bike_grips.jpg", "suspension-fork.jpg"),
            505: ("components/bike_grips.jpg", "carbon-handlebars.jpg"),
            506: ("components/bike_chain.jpg", "power-meter-crankset.jpg"),
            507: ("components/bike_tire.jpg", "tubeless-tire-set.jpg"),
            508: ("components/bike_chain.jpg", "chain-and-cassette-kit.jpg"),
            509: ("components/bike_grips.jpg", "pedal-system-clipless.jpg"),
            510: ("components/bike_grips.jpg", "saddle-performance.jpg"),
            
            # Sale Items (reuse existing S3 files)
            601: ("mountain_bikes/trek_fuel_ex.jpg", "trail-master-pro.jpg"),  # Same as 201
            602: ("electric_bikes/electric_bike_1.jpg", "urban-e-commuter-pro.jpg"),  # Same as 101
            603: ("accessories/bike_helmet.jpg", "pro-racing-helmet.jpg"),  # Same as 401
            604: ("components/bike_wheel.jpg", "carbon-wheelset.jpg"),  # Same as 501
        }
        
        uploaded_files = set()
        updated_products = 0
        
        for product_id, (local_path, s3_filename) in image_assignments.items():
            try:
                product = Product.objects.get(pk=product_id)
                local_file_path = f"media/products/{local_path}"
                s3_key = f"{s3_folder}{s3_filename}"
                
                # Upload file to S3 if not already uploaded
                if s3_filename not in uploaded_files and os.path.exists(local_file_path):
                    try:
                        self.stdout.write(f'Uploading {local_file_path} -> s3://{bucket_name}/{s3_key}')
                        
                        with open(local_file_path, 'rb') as file_data:
                            s3_client.upload_fileobj(
                                file_data,
                                bucket_name,
                                s3_key,
                                ExtraArgs={
                                    'ContentType': 'image/jpeg',
                                    'ACL': 'public-read'  # Make images publicly accessible
                                }
                            )
                        
                        uploaded_files.add(s3_filename)
                        self.stdout.write(self.style.SUCCESS(f'✓ Uploaded: {s3_filename}'))
                        
                    except ClientError as e:
                        self.stdout.write(self.style.ERROR(f'✗ Upload failed for {s3_filename}: {e}'))
                        continue
                
                # Update product image URL
                s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
                product.image_url = s3_url
                product.save()
                updated_products += 1
                
                self.stdout.write(f'✓ Updated {product.name}: {s3_url}')
                
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Product {product_id} not found'))
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f'⚠ Local file not found: {local_file_path}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Upload complete!'))
        self.stdout.write(f'📁 Uploaded {len(uploaded_files)} unique images to S3')
        self.stdout.write(f'🔗 Updated {updated_products} product URLs')
        self.stdout.write('')
        self.stdout.write('S3 Structure:')
        self.stdout.write(f'  Bucket: {bucket_name}')
        self.stdout.write(f'  Folder: {s3_folder}')
        self.stdout.write(f'  Files: {len(uploaded_files)} images')