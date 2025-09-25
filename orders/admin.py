from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    """Inline admin for order line items"""
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)
    extra = 0
    fields = ('product', 'size', 'quantity', 'lineitem_total')

    def lineitem_total(self, obj):
        """Display formatted line item total"""
        if obj.id:
            return f"€{obj.lineitem_total:.2f}"
        return "-"
    lineitem_total.short_description = "Line Total"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders"""
    inlines = (OrderLineItemAdminInline,)
    
    readonly_fields = ('order_number', 'date', 'updated', 'order_total',
                       'delivery_cost', 'grand_total', 'original_cart')

    fields = ('order_number', 'user_profile', 'status', 'date', 'updated',
              'full_name', 'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'order_total',
              'delivery_cost', 'grand_total', 'original_cart', 'stripe_pid')

    list_display = ('order_number', 'date', 'full_name', 'status',
                    'order_total_display', 'delivery_cost_display', 
                    'grand_total_display', 'total_items_display')

    list_filter = ('status', 'date', 'country')
    
    search_fields = ('order_number', 'full_name', 'email', 'user_profile__user__username')
    
    ordering = ('-date',)

    def order_total_display(self, obj):
        """Display formatted order total"""
        return f"€{obj.order_total:.2f}"
    order_total_display.short_description = "Order Total"
    order_total_display.admin_order_field = 'order_total'

    def delivery_cost_display(self, obj):
        """Display formatted delivery cost"""
        return f"€{obj.delivery_cost:.2f}"
    delivery_cost_display.short_description = "Delivery"
    delivery_cost_display.admin_order_field = 'delivery_cost'

    def grand_total_display(self, obj):
        """Display formatted grand total"""
        return f"€{obj.grand_total:.2f}"
    grand_total_display.short_description = "Grand Total"
    grand_total_display.admin_order_field = 'grand_total'

    def total_items_display(self, obj):
        """Display total number of items"""
        return obj.total_items
    total_items_display.short_description = "Items"

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after order creation"""
        readonly_fields = list(self.readonly_fields)
        if obj:  # Editing existing order
            readonly_fields.extend(['user_profile'])
        return readonly_fields


@admin.register(OrderLineItem)
class OrderLineItemAdmin(admin.ModelAdmin):
    """Admin interface for order line items"""
    list_display = ('order', 'product', 'size', 'quantity', 'lineitem_total_display')
    list_filter = ('order__date', 'product__category')
    search_fields = ('order__order_number', 'product__name', 'product__sku')
    readonly_fields = ('lineitem_total',)

    def lineitem_total_display(self, obj):
        """Display formatted line item total"""
        return f"€{obj.lineitem_total:.2f}"
    lineitem_total_display.short_description = "Line Total"
    lineitem_total_display.admin_order_field = 'lineitem_total'