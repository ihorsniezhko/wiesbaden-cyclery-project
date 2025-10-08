# Social Media Sharing - Wiesbaden Cyclery

## Overview
This document explains how social media sharing works for the Wiesbaden Cyclery website and how to troubleshoot issues.

## Open Graph (OG) Tags Implementation

### Product Pages
Product pages now include optimized OG tags for social media sharing:

- **og:title**: Product name only (e.g., "Carbon Handlebars")
- **og:site_name**: "Wiesbaden Cyclery" (automatically added by base template)
- **og:description**: Product description with price
- **og:image**: Full absolute URL to product image (or default store image)
- **og:type**: "product"
- **og:url**: Full URL to the product page

### Image Requirements
- **Format**: JPEG or PNG
- **Recommended Size**: 1200x630 pixels (1.91:1 ratio)
- **Minimum Size**: 600x315 pixels
- **Maximum Size**: 8MB
- **URL**: Must be absolute (https://domain.com/media/image.jpg)

## Social Media Platform Specifics

### WhatsApp
- Uses Open Graph tags
- Caches previews aggressively
- Shows: og:title, og:site_name, og:description, og:image

### Facebook
- Uses Open Graph tags
- Caches previews for 7 days
- Debug tool: https://developers.facebook.com/tools/debug/

### Twitter/X
- Uses Twitter Card tags (falls back to OG tags)
- Card type: summary_large_image
- Debug tool: https://cards-dev.twitter.com/validator

### LinkedIn
- Uses Open Graph tags
- Caches previews
- Post Inspector: https://www.linkedin.com/post-inspector/

## Clearing Social Media Caches

### Facebook/WhatsApp Cache
1. Go to: https://developers.facebook.com/tools/debug/
2. Enter your product URL
3. Click "Scrape Again" to refresh the cache
4. Verify the preview shows correct information

### Twitter Cache
1. Go to: https://cards-dev.twitter.com/validator
2. Enter your product URL
3. Click "Preview card"
4. Twitter will fetch fresh data

### LinkedIn Cache
1. Go to: https://www.linkedin.com/post-inspector/
2. Enter your product URL
3. Click "Inspect"
4. LinkedIn will refresh the cache

## Troubleshooting

### Issue: "Wiesbaden Cyclery" appears twice
**Cause**: Product template was including site name in og:title
**Solution**: Removed site name from og:title, letting og:site_name handle it

### Issue: Wrong image showing (default store image instead of product)
**Cause**: Image URL was relative, not absolute
**Solution**: Changed to use full absolute URLs with request.scheme and request.get_host

### Issue: Changes not appearing when sharing
**Cause**: Social media platforms cache OG tags
**Solution**: Use platform-specific debug tools to clear cache

### Issue: Image not displaying
**Possible causes**:
1. Image URL is not absolute
2. Image file is too large (>8MB)
3. Image is not publicly accessible
4. HTTPS certificate issues
5. Image dimensions are too small

## Testing Social Media Previews

### Before Deploying
1. Test locally with ngrok or similar tool
2. Verify all OG tags are present in page source
3. Check image URLs are absolute and accessible

### After Deploying
1. View page source and verify OG tags
2. Test with Facebook Debugger
3. Test with Twitter Card Validator
4. Share on WhatsApp to verify preview

### Verification Checklist
- [ ] og:title shows product name only
- [ ] og:site_name shows "Wiesbaden Cyclery"
- [ ] og:description includes product info and price
- [ ] og:image uses absolute URL (https://...)
- [ ] Product image displays (not default store image)
- [ ] og:type is set to "product"
- [ ] og:url is the full product page URL
- [ ] Image dimensions are 1200x630 or larger
- [ ] All meta tags visible in page source

## Implementation Details

### Product Detail Template
Location: `wiesbaden_cyclery_project/templates/products/product_detail.html`

Key blocks:
```django
{% block og_title %}{{ product.name }}{% endblock %}
{% block og_image %}{{ request.scheme }}://{{ request.get_host }}{{ product.image.url }}{% endblock %}
```

### Base Template
Location: `wiesbaden_cyclery_project/templates/base.html`

Provides default OG tags and og:site_name:
```html
<meta property="og:site_name" content="Wiesbaden Cyclery">
```

## Best Practices

1. **Always use absolute URLs for images**
2. **Keep og:title concise** (under 60 characters)
3. **Keep og:description informative** (under 200 characters)
4. **Use high-quality images** (1200x630 recommended)
5. **Test on multiple platforms** before major releases
6. **Clear caches** when making OG tag changes
7. **Monitor social shares** for issues

## Additional Resources

- [Open Graph Protocol](https://ogp.me/)
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [Twitter Card Validator](https://cards-dev.twitter.com/validator)
- [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/)
- [WhatsApp FAQ](https://faq.whatsapp.com/general/how-to-preview-links)
