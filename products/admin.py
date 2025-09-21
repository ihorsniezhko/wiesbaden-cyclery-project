"""
Admin configuration for products app
"""
from django.contrib import admin
from .models import Product, Category, Size, Review


class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category"""
    
    list_display = (
        'friendly_name',
        'name',
    )
    
    search_fields = ('name', 'friendly_name')
    ordering = ('friendly_name',)


class SizeAdmin(admin.ModelAdmin):
    """Admin configuration for Size"""
    
    list_display = (
        'display_name',
        'name',
        'sort_order',
    )
    
    list_editable = ('sort_order',)
    ordering = ('sort_order', 'name')


class ReviewInline(admin.TabularInline):
    """Inline admin for Reviews"""
    model = Review
    extra = 0
    readonly_fields = ('created_at',)


class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product"""
    
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'in_stock',
        'stock_quantity',
        'has_sizes',
        'created_at',
    )
    
    list_filter = (
        'category',
        'has_sizes',
        'in_stock',
        'created_at',
    )
    
    search_fields = (
        'name',
        'sku',
        'description',
    )
    
    list_editable = (
        'price',
        'in_stock',
        'stock_quantity',
    )
    
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'sku',
                'category',
                'description',
                'price',
                'rating'
            )
        }),
        ('Stock Management', {
            'fields': (
                'in_stock',
                'stock_quantity',
            )
        }),
        ('Size Configuration', {
            'fields': (
                'has_sizes',
                'sizes',
            )
        }),
        ('Bicycle Specifications', {
            'fields': (
                'frame_size',
                'wheel_size',
                'gear_system',
                'bicycle_features',
            ),
            'classes': ('collapse',),
        }),
        ('Images', {
            'fields': (
                'image',
                'image_url',
            )
        }),
    )
    
    filter_horizontal = ('sizes',)
    inlines = [ReviewInline]
    
    readonly_fields = ('created_at', 'updated_at')


class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review"""
    
    list_display = (
        'title',
        'product',
        'user',
        'rating',
        'created_at',
    )
    
    list_filter = (
        'rating',
        'created_at',
        'product__category',
    )
    
    search_fields = (
        'title',
        'comment',
        'product__name',
        'user__username',
    )
    
    readonly_fields = ('created_at',)
    
    ordering = ('-created_at',)


# Register models with admin
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Review, ReviewAdmin)