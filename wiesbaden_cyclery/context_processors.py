"""
Context processors for Wiesbaden Cyclery project.
"""
from django.conf import settings


def analytics(request):
    """
    Add analytics configuration to template context.
    """
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', ''),
        'FB_PIXEL_ID': getattr(settings, 'FB_PIXEL_ID', ''),
    }