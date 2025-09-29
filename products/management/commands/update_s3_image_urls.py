from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Update all product image URLs to point to new S3 images'

    def handle(self, *args, **options):
        # S3 base URL for the wiesbaden-cyclery-project bucket
        s3_base_url = 'https://wiesbaden-cyclery-project.s3.amazonaws.com/media/'
        
        # Mapping of product IDs to their new S3 image filenames
        product_image_mapping = {
            # ACCESSORIES (14 products)
            408: 'product_408_bike_computer_gps.jpg',
            411: 'product_411_bike_lock_security.jpg',
            7: 'product_007_cycling_gloves.jpg',
            405: 'product_405_cycling_gloves_pro.jpg',
            402: 'product_402_cycling_jersey_pro.jpg',
            409: 'product_409_cycling_shoes.jpg',
            412: 'product_412_cycling_sunglasses.jpg',
            406: 'product_406_frame_bag.jpg',
            404: 'product_404_led_light_set.jpg',
            410: 'product_410_multi_tool_kit.jpg',
            403: 'product_403_padded_cycling_shorts.jpg',
            6: 'product_006_premium_bike_helmet.jpg',
            401: 'product_401_pro_racing_helmet.jpg',
            407: 'product_407_water_bottle_set.jpg',
            
            # COMPONENTS (13 products)
            505: 'product_505_carbon_handlebars.jpg',
            501: 'product_501_carbon_wheelset.jpg',
            508: 'product_508_chain_and_cassette_kit.jpg',
            503: 'product_503_electronic_shifting_system.jpg',
            15: 'product_015_ergonomic_handlebar_grips.jpg',
            502: 'product_502_hydraulic_disc_brakes.jpg',
            509: 'product_509_pedal_system_clipless.jpg',
            506: 'product_506_power_meter_crankset.jpg',
            14: 'product_014_premium_bike_tire.jpg',
            510: 'product_510_saddle_performance.jpg',
            12: 'product_012_shimano_chain.jpg',
            504: 'product_504_suspension_fork.jpg',
            507: 'product_507_tubeless_tire_set.jpg',
            
            # ELECTRIC BIKES (9 products)
            5: 'product_005_bosch_performance_ebike.jpg',
            106: 'product_106_cargo_e_hauler.jpg',
            103: 'product_103_city_e_cruiser.jpg',
            107: 'product_107_fat_tire_e_adventure.jpg',
            105: 'product_105_folding_e_compact.jpg',
            102: 'product_102_mountain_e_explorer.jpg',
            104: 'product_104_performance_e_road.jpg',
            101: 'product_101_urban_e_commuter_pro.jpg',
            108: 'product_108_vintage_e_classic.jpg',
            
            # MOUNTAIN BIKES (9 products)
            204: 'product_204_all_mountain_explorer.jpg',
            203: 'product_203_cross_country_racer.jpg',
            206: 'product_206_downhill_destroyer.jpg',
            202: 'product_202_enduro_beast.jpg',
            3: 'product_003_giant_talon_1.jpg',
            205: 'product_205_hardtail_climber.jpg',
            208: 'product_208_plus_size_adventurer.jpg',
            201: 'product_201_trail_master_pro.jpg',
            207: 'product_207_trail_starter.jpg',
            
            # ROAD BIKES (8 products)
            301: 'product_301_aero_speed_demon.jpg',
            304: 'product_304_classic_steel_tourer.jpg',
            307: 'product_307_cyclocross_racer.jpg',
            302: 'product_302_endurance_cruiser.jpg',
            308: 'product_308_entry_level_roadie.jpg',
            303: 'product_303_gravel_adventure.jpg',
            305: 'product_305_time_trial_rocket.jpg',
            306: 'product_306_urban_commuter.jpg',
            
            # SALE ITEMS (7 products)
            604: 'product_604_carbon_wheelset_special_offer.jpg',
            17: 'product_017_clearance_cycling_gloves.jpg',
            16: 'product_016_discounted_road_bike_helmet.jpg',
            603: 'product_603_pro_racing_helmet_discount.jpg',
            18: 'product_018_special_offer_bike_chain.jpg',
            601: 'product_601_trail_master_pro_sale.jpg',
            602: 'product_602_urban_e_commuter_clearance.jpg'
        }
        
        self.stdout.write('UPDATING PRODUCT IMAGE URLs TO S3')
        self.stdout.write('='*80)
        
        updated_count = 0
        not_found_count = 0
        
        for product_id, filename in product_image_mapping.items():
            try:
                product = Product.objects.get(id=product_id)
                new_url = f'{s3_base_url}{filename}'
                
                # Update the image_url field
                old_url = product.image_url
                product.image_url = new_url
                product.save()
                
                self.stdout.write(f'✓ Product {product_id:3d} ({product.name[:30]:30s}): Updated to {filename}')
                if old_url:
                    self.stdout.write(f'    Old: {old_url[:60]}...')
                self.stdout.write(f'    New: {new_url}')
                
                updated_count += 1
                
            except Product.DoesNotExist:
                self.stdout.write(f'✗ Product {product_id} not found in database')
                not_found_count += 1
        
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(f'UPDATE SUMMARY:')
        self.stdout.write(f'Successfully updated: {updated_count}')
        self.stdout.write(f'Products not found: {not_found_count}')
        self.stdout.write(f'Total products processed: {len(product_image_mapping)}')
        self.stdout.write(f'{"="*80}')
        
        # Verify the updates
        self.stdout.write(f'\nVERIFICATION:')
        products_with_s3_urls = Product.objects.filter(image_url__startswith=s3_base_url).count()
        total_products = Product.objects.count()
        
        self.stdout.write(f'Products with S3 URLs: {products_with_s3_urls}/{total_products}')
        
        if products_with_s3_urls == len(product_image_mapping):
            self.stdout.write('✅ All mapped products now have S3 image URLs!')
        else:
            self.stdout.write('⚠️  Some products may still need URL updates')
        
        self.stdout.write(f'\nNEXT STEPS:')
        self.stdout.write(f'1. Verify images are accessible at: {s3_base_url}')
        self.stdout.write(f'2. Test website to ensure all product images load correctly')
        self.stdout.write(f'3. Clear any CDN/browser cache if needed')
        
        return f'Updated {updated_count}/{len(product_image_mapping)} product image URLs'