# S3 Image Upload Mapping

## Instructions
1. Upload these images to S3 bucket: `wiesbaden-cyclery-project`
2. Create folder: `product_images/`
3. Rename and upload the local images according to this mapping
4. Set public read permissions on all uploaded images

## Local Image → S3 Filename Mapping

### Electric Bikes (3 source images → 8 S3 files)
- `media/products/electric_bikes/electric_bike_1.jpg` → `urban-e-commuter-pro.jpg`
- `media/products/electric_bikes/electric_bike_2.jpg` → `mountain-e-explorer.jpg`
- `media/products/electric_bikes/bosch_ebike.jpg` → `city-e-cruiser.jpg`
- `media/products/electric_bikes/electric_bike_1.jpg` → `performance-e-road.jpg` (copy)
- `media/products/electric_bikes/electric_bike_2.jpg` → `folding-e-compact.jpg` (copy)
- `media/products/electric_bikes/bosch_ebike.jpg` → `cargo-e-hauler.jpg` (copy)
- `media/products/electric_bikes/electric_bike_1.jpg` → `fat-tire-e-adventure.jpg` (copy)
- `media/products/electric_bikes/electric_bike_2.jpg` → `vintage-e-classic.jpg` (copy)

### Mountain Bikes (3 source images → 8 S3 files)
- `media/products/mountain_bikes/trek_fuel_ex.jpg` → `trail-master-pro.jpg`
- `media/products/mountain_bikes/giant_talon.jpg` → `enduro-beast.jpg`
- `media/products/mountain_bikes/mountain_bike_1.jpg` → `cross-country-racer.jpg`
- `media/products/mountain_bikes/trek_fuel_ex.jpg` → `all-mountain-explorer.jpg` (copy)
- `media/products/mountain_bikes/giant_talon.jpg` → `hardtail-climber.jpg` (copy)
- `media/products/mountain_bikes/mountain_bike_1.jpg` → `downhill-destroyer.jpg` (copy)
- `media/products/mountain_bikes/trek_fuel_ex.jpg` → `trail-starter.jpg` (copy)
- `media/products/mountain_bikes/giant_talon.jpg` → `plus-size-adventurer.jpg` (copy)

### Road Bikes (2 source images → 8 S3 files)
- `media/products/road_bikes/specialized_allez.jpg` → `aero-speed-demon.jpg`
- `media/products/road_bikes/trek_domane.jpg` → `endurance-cruiser.jpg`
- `media/products/road_bikes/specialized_allez.jpg` → `gravel-adventure.jpg` (copy)
- `media/products/road_bikes/trek_domane.jpg` → `classic-steel-tourer.jpg` (copy)
- `media/products/road_bikes/specialized_allez.jpg` → `time-trial-rocket.jpg` (copy)
- `media/products/road_bikes/trek_domane.jpg` → `urban-commuter.jpg` (copy)
- `media/products/road_bikes/specialized_allez.jpg` → `cyclocross-racer.jpg` (copy)
- `media/products/road_bikes/trek_domane.jpg` → `entry-level-roadie.jpg` (copy)

### Accessories (6 source images → 12 S3 files)
- `media/products/accessories/bike_helmet.jpg` → `pro-racing-helmet.jpg`
- `media/products/accessories/cycling_gloves.jpg` → `cycling-jersey-pro.jpg`
- `media/products/accessories/cycling_gloves.jpg` → `padded-cycling-shorts.jpg` (copy)
- `media/products/accessories/bike_lights.jpg` → `led-light-set.jpg`
- `media/products/accessories/cycling_gloves.jpg` → `cycling-gloves.jpg` (copy)
- `media/products/accessories/bike_pump.jpg` → `frame-bag.jpg`
- `media/products/accessories/water_bottle.jpg` → `water-bottle-set.jpg`
- `media/products/accessories/bike_pump.jpg` → `bike-computer-gps.jpg` (copy)
- `media/products/accessories/cycling_gloves.jpg` → `cycling-shoes.jpg` (copy)
- `media/products/accessories/bike_pump.jpg` → `multi-tool-kit.jpg` (copy)
- `media/products/accessories/bike_lock.jpg` → `bike-lock-security.jpg`
- `media/products/accessories/bike_helmet.jpg` → `cycling-sunglasses.jpg` (copy)

### Components (4 source images → 10 S3 files)
- `media/products/components/bike_wheel.jpg` → `carbon-wheelset.jpg`
- `media/products/components/bike_grips.jpg` → `hydraulic-disc-brakes.jpg`
- `media/products/components/bike_grips.jpg` → `electronic-shifting-system.jpg` (copy)
- `media/products/components/bike_grips.jpg` → `suspension-fork.jpg` (copy)
- `media/products/components/bike_grips.jpg` → `carbon-handlebars.jpg` (copy)
- `media/products/components/bike_chain.jpg` → `power-meter-crankset.jpg`
- `media/products/components/bike_tire.jpg` → `tubeless-tire-set.jpg`
- `media/products/components/bike_chain.jpg` → `chain-and-cassette-kit.jpg` (copy)
- `media/products/components/bike_grips.jpg` → `pedal-system-clipless.jpg` (copy)
- `media/products/components/bike_grips.jpg` → `saddle-performance.jpg` (copy)

### Sale Items (reuse existing files - no additional uploads needed)
- `trail-master-pro.jpg` (already uploaded)
- `urban-e-commuter-pro.jpg` (already uploaded)
- `pro-racing-helmet.jpg` (already uploaded)
- `carbon-wheelset.jpg` (already uploaded)

## Summary
- **Total local source images**: 18 unique files
- **Total S3 files needed**: 46 files (with copies/renames)
- **S3 bucket**: `wiesbaden-cyclery-project`
- **S3 folder**: `product_images/`

## After Upload
Run this command on production to verify all images are accessible:
```bash
heroku run python manage.py verify_s3_images --app wiesbaden-cyclery-project
```