# Facebook Pixel Setup - Wiesbaden Cyclery

## Overview
Facebook Pixel support has been implemented in the Wiesbaden Cyclery project to enable tracking of user interactions and conversions for Facebook advertising campaigns.

## Configuration

### 1. Environment Variables
Add your Facebook Pixel ID to the `.env` file:

```env
# Analytics (optional)
GA_MEASUREMENT_ID=G-XXXXXXXXXX
FB_PIXEL_ID=123456789012345
```

### 2. Settings Configuration
The Facebook Pixel ID is automatically loaded from the environment variables in `settings.py`:

```python
# Analytics Configuration
GA_MEASUREMENT_ID = config('GA_MEASUREMENT_ID', default='')
FB_PIXEL_ID = config('FB_PIXEL_ID', default='')
```

### 3. Template Integration
The Facebook Pixel base code is automatically included in `base.html` when `FB_PIXEL_ID` is configured.

## Usage

### Basic Page View Tracking
Page views are automatically tracked when the Facebook Pixel ID is configured. No additional code needed.

### Custom Event Tracking
Use the `facebook_pixel_events` block in templates to add custom event tracking:

```html
{% block facebook_pixel_events %}
<script>
// Track product view
fbq('track', 'ViewContent', {
    content_type: 'product',
    content_ids: ['{{ product.id }}'],
    content_name: '{{ product.name }}',
    content_category: '{{ product.category.name }}',
    value: {{ product.price }},
    currency: 'EUR'
});
</script>
{% endblock %}
```

### Common Facebook Pixel Events

#### 1. Product View (product_detail.html)
```html
{% block facebook_pixel_events %}
<script>
fbq('track', 'ViewContent', {
    content_type: 'product',
    content_ids: ['{{ product.id }}'],
    content_name: '{{ product.name }}',
    content_category: '{{ product.category.name }}',
    value: {{ product.price }},
    currency: 'EUR'
});
</script>
{% endblock %}
```

#### 2. Add to Cart (cart.html or AJAX)
```javascript
fbq('track', 'AddToCart', {
    content_type: 'product',
    content_ids: [product_id],
    content_name: product_name,
    value: product_price,
    currency: 'EUR'
});
```

#### 3. Purchase (order_confirmation.html)
```html
{% block facebook_pixel_events %}
<script>
fbq('track', 'Purchase', {
    value: {{ order.total }},
    currency: 'EUR',
    content_type: 'product',
    content_ids: [{% for item in order.items.all %}'{{ item.product.id }}'{% if not forloop.last %},{% endif %}{% endfor %}],
    contents: [
        {% for item in order.items.all %}
        {
            'id': '{{ item.product.id }}',
            'quantity': {{ item.quantity }},
            'item_price': {{ item.product.price }}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ]
});
</script>
{% endblock %}
```

#### 4. Lead Generation (signup.html)
```html
{% block facebook_pixel_events %}
<script>
fbq('track', 'Lead');
</script>
{% endblock %}
```

#### 5. Search (products.html with search)
```html
{% block facebook_pixel_events %}
{% if request.GET.q %}
<script>
fbq('track', 'Search', {
    search_string: '{{ request.GET.q }}'
});
</script>
{% endif %}
{% endblock %}
```

## Testing

### 1. Facebook Pixel Helper
Install the Facebook Pixel Helper browser extension to verify pixel firing.

### 2. Events Manager
Check Facebook Events Manager to see real-time pixel events.

### 3. Test Events
Use Facebook's Test Events tool to verify pixel implementation.

## Privacy Compliance

### GDPR Considerations
- The pixel only loads when a valid `FB_PIXEL_ID` is configured
- Consider implementing consent management for EU users
- Update privacy policy to mention Facebook tracking

### Cookie Consent Integration
The existing cookie consent banner should cover Facebook Pixel usage. Update the privacy policy link to explain Facebook tracking.

## Troubleshooting

### Pixel Not Loading
1. Check that `FB_PIXEL_ID` is set in `.env`
2. Verify the ID is not the placeholder value
3. Check browser console for JavaScript errors

### Events Not Firing
1. Use Facebook Pixel Helper to debug
2. Check that custom events are in the correct template block
3. Verify event parameters match Facebook's requirements

## Best Practices

1. **Use Standard Events**: Stick to Facebook's standard events when possible
2. **Include Value**: Always include monetary value for commerce events
3. **Test Thoroughly**: Use Facebook's testing tools before going live
4. **Monitor Performance**: Regularly check Events Manager for data quality
5. **Privacy First**: Ensure compliance with local privacy laws

## Getting Your Facebook Pixel ID

1. Go to Facebook Business Manager
2. Navigate to Events Manager
3. Create a new Pixel or select existing one
4. Copy the Pixel ID (15-16 digit number)
5. Add to your `.env` file

Replace `YOUR_PIXEL_ID_HERE` with your actual Facebook Pixel ID to activate tracking.