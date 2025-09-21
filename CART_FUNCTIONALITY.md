# Shopping Cart Functionality - Stage 4

## Overview

The shopping cart system provides comprehensive e-commerce cart functionality with support for both authenticated users and anonymous sessions. The system includes automatic cart merging when users log in and intelligent delivery cost calculations.

## Features Implemented

### 1. Cart Models

#### Cart Model
- **User Association**: Links to authenticated users via OneToOneField
- **Session Support**: Uses session keys for anonymous users
- **Automatic Calculations**: Real-time subtotal, delivery cost, and total calculations
- **Item Management**: Tracks total items and provides cart clearing functionality

#### CartItem Model
- **Product Integration**: Links to products with optional size selection
- **Quantity Management**: Supports quantity updates with validation
- **Line Total Calculation**: Automatic price × quantity calculations
- **Size Validation**: Ensures size compatibility with products

### 2. Cart Logic & Calculations

#### Delivery Cost Logic
- **Free Delivery Threshold**: Orders over €50 qualify for free delivery
- **Standard Delivery**: €4.99 for orders under €50
- **Real-time Updates**: Delivery cost recalculates automatically

#### Session Management
- **Anonymous Carts**: Session-based cart storage for non-authenticated users
- **User Carts**: Database-linked carts for authenticated users
- **Cart Merging**: Automatic merge when anonymous users log in
- **Persistence**: Carts persist across browser sessions

### 3. Cart Views & URLs

#### Main Views
- `cart_view`: Display cart contents with management controls
- `add_to_cart_view`: Add products with size and quantity selection
- `update_cart_view`: Modify item quantities
- `remove_from_cart_view`: Remove specific items
- `clear_cart_view`: Empty entire cart

#### AJAX Views
- `ajax_add_to_cart`: Dynamic cart updates without page refresh
- `ajax_update_cart`: Real-time quantity modifications
- `cart_summary_ajax`: Get current cart totals

#### URL Patterns
```
/cart/                          # Main cart view
/cart/add/<product_id>/         # Add product to cart
/cart/update/<product_id>/      # Update cart item
/cart/remove/<product_id>/      # Remove cart item
/cart/clear/                    # Clear entire cart
/cart/ajax/add/<product_id>/    # AJAX add to cart
/cart/ajax/update/<product_id>/ # AJAX update cart
/cart/ajax/summary/             # AJAX cart summary
```

### 4. Template Integration

#### Cart Template (`cart.html`)
- **Responsive Design**: Bootstrap 4 styling with mobile support
- **Item Management**: Quantity controls with +/- buttons
- **Real-time Updates**: JavaScript-powered quantity adjustments
- **Cost Breakdown**: Clear display of subtotal, delivery, and total
- **Empty State**: Helpful messaging when cart is empty

#### Navigation Integration
- **Cart Badge**: Shows item count in navigation
- **Quick Access**: Direct link to cart from any page
- **Context Processor**: Cart information available in all templates

#### Product Detail Integration
- **Add to Cart Form**: Size selection and quantity controls
- **Validation**: Client-side and server-side validation
- **User Feedback**: Success and error messages
- **Redirect Options**: Return to product or go to cart

### 5. Utility Functions

#### Core Utilities (`utils.py`)
- `get_or_create_cart()`: Smart cart retrieval/creation
- `add_to_cart()`: Add products with validation
- `update_cart_item()`: Modify quantities safely
- `remove_from_cart()`: Remove items with confirmation
- `clear_cart()`: Empty cart completely
- `merge_carts()`: Combine anonymous and user carts

### 6. Admin Interface

#### Cart Management
- **Cart Overview**: List all carts with user/session info
- **Item Details**: Inline editing of cart items
- **Totals Display**: Real-time calculation display
- **Search & Filter**: Find carts by user or session

#### CartItem Management
- **Product Details**: Full product and size information
- **Quantity Tracking**: Current quantities and line totals
- **Owner Information**: Cart owner identification

### 7. Testing Coverage

#### Model Tests (15 tests)
- Cart creation for users and sessions
- Cart calculations and totals
- CartItem functionality and validation
- Utility function testing

#### View Tests (11 tests)
- Cart display and management
- Add/update/remove operations
- AJAX functionality
- Error handling and validation

#### Integration Tests (2 tests)
- Cart merging on user login
- Delivery cost calculations
- Cross-session functionality

**Total: 26 comprehensive tests covering all cart functionality**

## Technical Implementation

### Context Processor
The cart context processor (`cart_contents`) makes cart information available in all templates:
- `cart`: Current cart object
- `cart_items`: List of cart items
- `cart_total_items`: Total item count
- `cart_subtotal`: Subtotal before delivery
- `cart_delivery_cost`: Delivery cost
- `cart_total`: Final total including delivery

### JavaScript Integration
Client-side functionality includes:
- Quantity increment/decrement controls
- Form validation and submission
- Real-time total updates
- AJAX cart operations

### Error Handling
Comprehensive error handling for:
- Invalid product/size combinations
- Quantity validation (1-99 range)
- Session management issues
- Database operation failures

## Usage Examples

### Adding Items to Cart
```python
# Via view
POST /cart/add/123/
{
    'quantity': 2,
    'size': 456,
    'redirect_to': 'cart'
}

# Via utility function
from shopping_cart.utils import add_to_cart
cart_item = add_to_cart(request, product, size, quantity)
```

### AJAX Operations
```javascript
// Add to cart via AJAX
fetch('/cart/ajax/add/123/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        quantity: 2,
        size: 456
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        updateCartBadge(data.cart_total_items);
    }
});
```

### Template Usage
```html
<!-- Display cart info -->
<span class="badge">{{ cart_total_items }}</span>
<p>Total: €{{ cart_total|floatformat:2 }}</p>

<!-- Add to cart form -->
<form method="POST" action="{% url 'shopping_cart:add_to_cart' product.id %}">
    {% csrf_token %}
    <select name="size">
        {% for size in product.sizes.all %}
            <option value="{{ size.id }}">{{ size.display_name }}</option>
        {% endfor %}
    </select>
    <input type="number" name="quantity" value="1" min="1" max="99">
    <button type="submit">Add to Cart</button>
</form>
```

## Security Considerations

- **CSRF Protection**: All forms include CSRF tokens
- **Input Validation**: Server-side validation for all inputs
- **Session Security**: Secure session handling for anonymous carts
- **SQL Injection Prevention**: Django ORM prevents SQL injection
- **XSS Protection**: Template auto-escaping prevents XSS

## Performance Optimizations

- **Database Queries**: Optimized with select_related() for cart items
- **Context Processor**: Efficient cart data retrieval
- **AJAX Operations**: Reduce page reloads for better UX
- **Template Caching**: Cart totals cached in context processor

## Future Enhancements

Potential improvements for future stages:
- Cart item expiration/cleanup
- Saved carts for later
- Cart sharing functionality
- Bulk operations (add multiple items)
- Cart analytics and reporting
- Integration with inventory management
- Advanced pricing rules and discounts

## Dependencies

- Django 3.2+
- Bootstrap 4 (for styling)
- jQuery (for JavaScript functionality)
- Products app (for product integration)
- Accounts app (for user management)

## Files Modified/Created

### New Files
- `shopping_cart/models.py` - Cart and CartItem models
- `shopping_cart/views.py` - Cart management views
- `shopping_cart/urls.py` - URL patterns
- `shopping_cart/utils.py` - Utility functions
- `shopping_cart/context_processors.py` - Template context
- `shopping_cart/admin.py` - Admin interface
- `shopping_cart/tests.py` - Comprehensive test suite
- `templates/shopping_cart/cart.html` - Cart template

### Modified Files
- `wiesbaden_cyclery/settings.py` - Added app and context processor
- `wiesbaden_cyclery/urls.py` - Added cart URLs
- `templates/base.html` - Added cart navigation
- `templates/products/product_detail.html` - Added cart functionality

This comprehensive cart system provides a solid foundation for the e-commerce platform and integrates seamlessly with the existing product catalog and user management systems.