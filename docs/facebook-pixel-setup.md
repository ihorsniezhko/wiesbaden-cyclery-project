# 📊 Facebook Pixel & Analytics

## Configuration

Add to `.env`:
```env
FB_PIXEL_ID=123456789012345
GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

## Getting Your IDs

### Facebook Pixel
1. Go to Facebook Business Manager → Events Manager
2. Create or select Pixel
3. Copy 15-16 digit Pixel ID

### Google Analytics
1. Go to Google Analytics → Admin → Data Streams
2. Copy Measurement ID (starts with G-)

## Usage

### Automatic Tracking
Page views tracked automatically when IDs configured.

### Custom Events

Add to templates using `facebook_pixel_events` block:

```html
{% block facebook_pixel_events %}
<script>
// Product view
fbq('track', 'ViewContent', {
    content_ids: ['{{ product.id }}'],
    content_name: '{{ product.name }}',
    value: {{ product.price }},
    currency: 'EUR'
});
</script>
{% endblock %}
```

### Standard Events

| Event | When to Use |
|-------|-------------|
| ViewContent | Product detail page |
| AddToCart | Add to cart action |
| Purchase | Order confirmation |
| Lead | Newsletter signup |
| Search | Product search |

## Testing

1. Install Facebook Pixel Helper extension
2. Visit your site
3. Check pixel fires correctly
4. View Events Manager for real-time data

## Privacy

- Pixel loads only when configured
- Update privacy policy to mention tracking
- Consider GDPR consent management
- Cookie consent banner covers tracking

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pixel not loading | Check `FB_PIXEL_ID` in .env |
| Events not firing | Use Pixel Helper to debug |
| Wrong data | Verify event parameters |
