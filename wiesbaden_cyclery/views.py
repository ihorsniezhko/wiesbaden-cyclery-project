"""
Main views for Wiesbaden Cyclery
"""
from django.shortcuts import render


def index(request):
    """
    Homepage view
    """
    return render(request, 'home/index.html')