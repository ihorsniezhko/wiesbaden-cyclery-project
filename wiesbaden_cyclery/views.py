"""
Main views for Wiesbaden Cyclery
"""
from django.shortcuts import render


def index(request):
    """
    Homepage view
    """
    return render(request, 'home/index.html')


def privacy_policy(request):
    """A view to return the privacy policy page"""
    context = {
        'last_updated': 'January 1, 2025',
    }
    return render(request, 'legal/privacy_policy.html', context)


def terms_of_service(request):
    """A view to return the terms of service page"""
    context = {
        'last_updated': 'January 1, 2025',
    }
    return render(request, 'legal/terms_of_service.html', context)


def cookie_settings(request):
    """A view to return the cookie settings page"""
    return render(request, 'legal/cookie_settings.html')