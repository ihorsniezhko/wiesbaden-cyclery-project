# Social Media Sharing - Wiesbaden Cyclery

## Overview
Wiesbaden Cyclery implements Open Graph (OG) and Twitter Card meta tags for optimal social media sharing across all platforms.

## Implementation

### OG Tags Structure
All pages include properly configured meta tags:
- **og:title**: Descriptive page title (without site name to avoid duplication)
- **og:site_name**: "Wiesbaden Cyclery" (added automatically)
- **og:description**: Page-specific description
- **og:image**: Absolute URL to product image or default store image
- **og:type**: "product" for products, "website" for other pages
- **og:url**: Full canonical URL

### Image Requirements
- **Format**: JPEG or PNG
- **Size**: 1200x630px recommended (1.91:1 ratio)
- **URL**: Must be absolute (https://...)

## Platform Support
- **Facebook/WhatsApp**: Uses OG tags, caches for 7+ days
- **Twitter/X**: Uses Twitter Cards (falls back to OG tags)
- **LinkedIn**: Uses OG tags, caches previews

## Clearing Social Media Caches

**Important**: Social platforms cache previews. After making changes, clear caches:

- **Facebook/WhatsApp**: https://developers.facebook.com/tools/debug/ → "Scrape Again"
- **Twitter**: https://cards-dev.twitter.com/validator → "Preview card"
- **LinkedIn**: https://www.linkedin.com/post-inspector/ → "Inspect"

## Troubleshooting

### Common Issues

**"Wiesbaden Cyclery" appears twice**
- **Cause**: Site name included in og:title
- **Solution:** Fixed - og:title now excludes site name

**Wrong image showing**
- **Cause**: Relative image URLs or missing product images
- **Solution:** Fixed - Uses absolute AWS S3 URLs for product images

**Changes not appearing**
- **Cause**: Social media cache
- **Solution**: Clear cache using platform debug tools (see above)

### Verification Checklist
- [x] og:title excludes "Wiesbaden Cyclery"
- [x] og:site_name shows "Wiesbaden Cyclery"
- [x] og:image uses absolute URL (https://...)
- [x] Product images load from AWS S3
- [x] All meta tags visible in page source

## Technical Implementation

### Key Templates
- **Base**: `templates/base.html` - Default OG tags and og:site_name
- **Home**: `templates/home/index.html` - Home page overrides
- **Products**: `templates/products/products.html` - Category/search overrides  
- **Product Detail**: `templates/products/product_detail.html` - Product-specific tags

### Example
```django
{% block og_title %}{{ product.name }}{% endblock %}
{% block og_image %}{{ product.image.url }}{% endblock %}
```

## Resources
- [Open Graph Protocol](https://ogp.me/)
- [Facebook Debugger](https://developers.facebook.com/tools/debug/)
- [Twitter Validator](https://cards-dev.twitter.com/validator)
- [LinkedIn Inspector](https://www.linkedin.com/post-inspector/)
