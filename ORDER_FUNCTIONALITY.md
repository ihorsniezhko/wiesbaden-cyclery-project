# Order Processing and Checkout Workflow - Stage 5

## Overview

The order processing system provides comprehensive e-commerce order management functionality, including checkout workflow, order tracking, and order history management. The system supports both authenticated users and guest checkout, with automatic user profile integration when available.

## Features Implemented

### 1. Order Models

#### Order Model
- **Unique Order Numbers**: UUID-based order number generation
- **Customer Information**: Full name, email, phone number storage
- **Delivery Address**: Complete address with country support via django-countries
- **Order Totals**: Automatic calculation of subtotal, delivery cost, and grand total
- **Status Tracking**: Order status progression (pending → processing → shipped → delivered)
- **User Integration**: Optional linking to UserProfile for authenticated users
- **Audit Trail**: Created and updated timestamps for order tracking

#### OrderLineItem Model
- **Product Integration**: Links to products with optional size selection
- **Quantity Management**: Supports quantity tracking with validation
- **Line Total Calculation**: Automatic price × quantity calculations
- **Order Integration**: Automatic order total updates via Django signals

### 2. Order Logic & Calculations

#### Order Total Calculations
- **Subtotal**: Sum of all line item totals
- **Delivery Cost**: €4.99 standard delivery, free over €50
- **Grand Total**: Subtotal + delivery cost
- **Real-time Updates**: Automatic recalculation when line items change

#### Order Number Generation
- **UUID-based**: 32-character unique identifiers
- **Collision-resistant**: Guaranteed uniqueness across all orders
- **User-friendly**: Uppercase format for easy communication

#### Stock Management
- **Stock Validation**: Checks product availability during checkout
- **Stock Updates**: Automatic stock reduction after successful orders
- **Stock Restoration**: Ability to restore stock for cancelled orders

### 3. Checkout Workflow

#### Checkout Process
1. **Cart Validation**: Ensures cart is not empty and items are in stock
2. **Form Collection**: Customer and delivery information collection
3. **Order Creation**: Converts cart contents to order with line items
4. **Stock Updates**: Reduces product stock quantities
5. **Cart Clearing**: Empties cart after successful order creation
6. **Confirmation**: Redirects to order confirmation page

#### Form Validation
- **Required Fields**: Full name, email, address validation
- **Email Cleaning**: Automatic email normalization (lowercase, trimmed)
- **Name Validation**: Ensures first and last name provided
- **Phone Validation**: Cleans and validates phone number format
- **Address Validation**: Ensures complete delivery address

#### User Profile Integration
- **Auto-fill**: Pre-populates checkout form with saved profile data
- **Profile Linking**: Associates orders with user profiles when authenticated
- **Guest Checkout**: Supports anonymous checkout without registration

### 4. Order Management Views

#### Checkout Views
- `checkout`: Main checkout form and processing
- `order_confirmation`: Order confirmation display
- `checkout_summary_ajax`: AJAX endpoint for checkout totals

#### Order History Views
- `order_history`: Paginated order history for authenticated users
- `order_detail`: Detailed order view with status timeline
- `order_tracking`: Guest order tracking by order number and email

#### AJAX Views
- `order_status_ajax`: Real-time order status updates
- `checkout_summary_ajax`: Dynamic checkout total calculations

### 5. Template System

#### Checkout Templates
- **Responsive Design**: Bootstrap 4 styling with mobile optimization
- **Order Summary**: Side-by-side cart summary during checkout
- **Form Validation**: Client-side and server-side validation
- **Loading States**: Visual feedback during form submission
- **Error Handling**: Clear error messages and validation feedback

#### Order Management Templates
- **Order History**: Searchable, paginated order list
- **Order Detail**: Comprehensive order information display
- **Order Tracking**: Guest-friendly order status checking
- **Status Timeline**: Visual progress indicators for order status

#### Navigation Integration
- **User Menu**: Order history link in user dropdown
- **Track Order**: Public order tracking link in main navigation
- **Responsive**: Mobile-friendly navigation and layouts

### 6. Order Status System

#### Status Progression
1. **Pending**: Order placed, awaiting processing
2. **Processing**: Order being prepared for shipment
3. **Shipped**: Order dispatched, in transit
4. **Delivered**: Order successfully delivered
5. **Cancelled**: Order cancelled (with stock restoration)

#### Status Display
- **Badge System**: Color-coded status badges
- **Timeline View**: Visual progress timeline in order details
- **Auto-refresh**: AJAX-powered status updates
- **Estimated Delivery**: Context-aware delivery estimates

### 7. Utility Functions

#### Core Utilities (`utils.py`)
- `create_order_from_cart()`: Convert cart to order
- `validate_order_data()`: Comprehensive order validation
- `update_product_stock()`: Stock management after orders
- `get_user_orders()`: Retrieve user's order history
- `get_order_summary()`: Format order data for display
- `format_order_for_email()`: Prepare order data for email templates

#### Stock Management
- `update_product_stock()`: Reduce stock after order creation
- `restore_product_stock()`: Restore stock for cancelled orders
- Stock validation during checkout process

### 8. Admin Interface

#### Order Management
- **Order Overview**: List all orders with key information
- **Inline Line Items**: Edit order contents directly
- **Status Management**: Update order status with dropdown
- **Search & Filter**: Find orders by number, customer, or status
- **Readonly Fields**: Protect calculated fields from manual editing

#### Order Analytics
- **Total Calculations**: Real-time order total displays
- **Item Counts**: Total items per order
- **Customer Information**: Complete customer details
- **Order Timeline**: Created and updated timestamps

### 9. Testing Coverage

#### Model Tests (8 tests)
- Order creation and validation
- Order number generation uniqueness
- Order total calculations
- Delivery cost logic
- Line item functionality
- Status badge display

#### View Tests (10 tests)
- Checkout workflow (empty cart, with items, form submission)
- Order confirmation display
- Order history (authenticated/anonymous access)
- Order tracking (GET/POST, valid/invalid data)
- AJAX endpoints

#### Form Tests (3 tests)
- Valid form data processing
- Invalid form data handling
- Email cleaning and validation

#### Integration Tests (1 test)
- Complete checkout workflow
- Cart-to-order conversion
- Stock management
- Cart clearing

**Total: 22 comprehensive tests covering all order functionality**

## Technical Implementation

### Database Schema
```sql
-- Order table with customer and delivery information
Order:
- order_number (CharField, unique, 32 chars)
- user_profile (ForeignKey to UserProfile, optional)
- full_name, email, phone_number (customer info)
- street_address1, street_address2, town_or_city, county, postcode, country (delivery)
- order_total, delivery_cost, grand_total (DecimalFields)
- status (CharField with choices)
- date, updated (DateTimeFields)
- original_cart (TextField, JSON)
- stripe_pid (CharField, for future payment integration)

-- Order line items
OrderLineItem:
- order (ForeignKey to Order)
- product (ForeignKey to Product)
- size (ForeignKey to Size, optional)
- quantity (PositiveIntegerField)
- lineitem_total (DecimalField, calculated)
```

### Signal Integration
```python
# Automatic order total updates
@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    instance.order.update_total()
```

### URL Structure
```
/orders/checkout/                    # Checkout form
/orders/confirmation/<order_number>/ # Order confirmation
/orders/history/                     # Order history (auth required)
/orders/detail/<order_number>/       # Order detail (auth required)
/orders/tracking/                    # Guest order tracking
/orders/ajax/status/<order_number>/  # AJAX status endpoint
/orders/ajax/checkout-summary/       # AJAX checkout summary
```

## Usage Examples

### Creating an Order from Cart
```python
from orders.utils import create_order_from_cart
from orders.forms import OrderForm

# Process checkout form
form = OrderForm(request.POST)
if form.is_valid():
    order = create_order_from_cart(request, form)
    update_product_stock(order)
    clear_cart(request)
    return redirect('orders:order_confirmation', order_number=order.order_number)
```

### Order Status Updates
```python
# Update order status
order = Order.objects.get(order_number='ABC123...')
order.status = 'shipped'
order.save()

# Get status badge class
badge_class = order.get_status_display_badge()  # Returns 'badge-primary'
```

### Order Tracking
```python
# Track order by number and email
try:
    order = Order.objects.get(
        order_number=order_number.upper(),
        email=email.lower()
    )
    return render(request, 'orders/tracking.html', {'order': order})
except Order.DoesNotExist:
    return render(request, 'orders/tracking.html', {
        'error': 'Order not found'
    })
```

### AJAX Status Updates
```javascript
// Auto-refresh order status
setInterval(function() {
    fetch(`/orders/ajax/status/${orderNumber}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.status !== currentStatus) {
                location.reload();
            }
        });
}, 60000);
```

## Security Considerations

- **CSRF Protection**: All forms include CSRF tokens
- **Input Validation**: Server-side validation for all form inputs
- **Permission Checks**: Users can only view their own orders
- **SQL Injection Prevention**: Django ORM prevents SQL injection
- **XSS Protection**: Template auto-escaping prevents XSS
- **Order Access Control**: Order number + email verification for guests

## Performance Optimizations

- **Database Queries**: Optimized with select_related() for order items
- **Pagination**: Order history paginated for large datasets
- **AJAX Updates**: Reduce page reloads for status updates
- **Template Caching**: Efficient template rendering
- **Index Optimization**: Database indexes on frequently queried fields

## Integration Points

### Shopping Cart Integration
- Seamless cart-to-order conversion
- Cart validation before checkout
- Automatic cart clearing after order creation
- Size and quantity preservation

### User Profile Integration
- Automatic form pre-population
- Order history association
- Profile data synchronization
- Guest checkout support

### Product Integration
- Stock validation and updates
- Product information preservation
- Size selection support
- Price calculation accuracy

## Future Enhancements

Potential improvements for future stages:
- Email notifications for order status changes
- Order modification and cancellation
- Bulk order operations
- Order export functionality
- Advanced order analytics
- Integration with shipping providers
- Order invoice generation
- Return and refund management

## Dependencies

- Django 3.2+
- django-countries (for country field)
- Bootstrap 4 (for styling)
- jQuery (for JavaScript functionality)
- Products app (for product integration)
- Shopping Cart app (for cart conversion)
- Accounts app (for user profile integration)

## Files Created/Modified

### New Files
- `orders/models.py` - Order and OrderLineItem models
- `orders/views.py` - Order management views
- `orders/urls.py` - URL patterns
- `orders/forms.py` - Order forms
- `orders/utils.py` - Utility functions
- `orders/admin.py` - Admin interface
- `orders/tests.py` - Comprehensive test suite
- `templates/orders/checkout.html` - Checkout template
- `templates/orders/order_confirmation.html` - Confirmation template
- `templates/orders/order_history.html` - Order history template
- `templates/orders/order_detail.html` - Order detail template
- `templates/orders/order_tracking.html` - Order tracking template

### Modified Files
- `wiesbaden_cyclery/settings.py` - Added orders app
- `wiesbaden_cyclery/urls.py` - Added order URLs
- `templates/base.html` - Added order navigation links
- `templates/shopping_cart/cart.html` - Added checkout button

This comprehensive order processing system provides a solid foundation for e-commerce operations and integrates seamlessly with the existing shopping cart and user management systems. The system is well-tested, documented, and ready for payment integration in Stage 6.