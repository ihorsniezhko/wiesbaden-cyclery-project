"""
URL patterns for accounts app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
]