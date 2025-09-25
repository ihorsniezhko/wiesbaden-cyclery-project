"""
Context processors for products app
"""
from .models import Category


def categories(request):
    """
    Make categories available in all templates
    """
    return {
        'all_categories': Category.objects.all().order_by('friendly_name')
    }