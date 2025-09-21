"""
Admin configuration for accounts app
"""
from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile"""
    
    list_display = (
        'user',
        'get_full_name',
        'default_phone_number',
        'default_town_or_city',
        'default_country'
    )
    
    list_filter = ('default_country', 'default_town_or_city')
    
    search_fields = (
        'user__username',
        'user__email',
        'first_name',
        'last_name',
        'default_phone_number'
    )
    
    ordering = ('user__username',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'first_name', 'last_name')
        }),
        ('Contact Information', {
            'fields': ('default_phone_number',)
        }),
        ('Default Delivery Information', {
            'fields': (
                'default_street_address1',
                'default_street_address2',
                'default_town_or_city',
                'default_county',
                'default_postcode',
                'default_country'
            )
        }),
    )


admin.site.register(UserProfile, UserProfileAdmin)