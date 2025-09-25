from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ('added_at', 'line_total')
    fields = ('product', 'size', 'quantity', 'added_at', 'line_total')

    def line_total(self, obj):
        """Display line total for each cart item"""
        if obj.id:
            return f"€{obj.line_total:.2f}"
        return "-"
    line_total.short_description = "Line Total"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for shopping carts"""
    list_display = ('__str__', 'user', 'session_key_short', 'total_items', 'subtotal_display', 'total_display', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'session_key')
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'subtotal_display', 'delivery_cost_display', 'total_display')
    inlines = [CartItemInline]

    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'session_key')
        }),
        ('Cart Totals', {
            'fields': ('total_items', 'subtotal_display', 'delivery_cost_display', 'total_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def session_key_short(self, obj):
        """Display shortened session key"""
        if obj.session_key:
            return f"{obj.session_key[:8]}..."
        return "-"
    session_key_short.short_description = "Session"

    def subtotal_display(self, obj):
        """Display formatted subtotal"""
        return f"€{obj.subtotal:.2f}"
    subtotal_display.short_description = "Subtotal"

    def delivery_cost_display(self, obj):
        """Display formatted delivery cost"""
        return f"€{obj.delivery_cost:.2f}"
    delivery_cost_display.short_description = "Delivery"

    def total_display(self, obj):
        """Display formatted total"""
        return f"€{obj.total:.2f}"
    total_display.short_description = "Total"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for cart items"""
    list_display = ('__str__', 'cart_owner', 'product', 'size', 'quantity', 'line_total_display', 'added_at')
    list_filter = ('added_at', 'product__category')
    search_fields = ('product__name', 'cart__user__username', 'cart__session_key')
    readonly_fields = ('added_at', 'line_total_display')

    def cart_owner(self, obj):
        """Display cart owner information"""
        if obj.cart.user:
            return obj.cart.user.username
        return f"Anonymous ({obj.cart.session_key[:8]}...)"
    cart_owner.short_description = "Cart Owner"

    def line_total_display(self, obj):
        """Display formatted line total"""
        return f"€{obj.line_total:.2f}"
    line_total_display.short_description = "Line Total"