"""wiesbaden_cyclery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Import test view
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from test_stripe_simple_view import simple_stripe_test
from debug_webhook import debug_stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('shopping_cart.urls')),
    path('orders/', include('orders.urls')),
    path('test-stripe-simple/', simple_stripe_test, name='test_stripe_simple'),
    path('debug-wh/', debug_stripe_webhook, name='debug_webhook'),
    path('', views.index, name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
