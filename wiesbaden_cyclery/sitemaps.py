from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Category


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return [
            'home',
            'products',
            'privacy_policy',
            'terms_of_service',
            'cookie_settings',
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Sitemap for product pages"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(in_stock=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('product_detail', args=[obj.pk])


class CategorySitemap(Sitemap):
    """Sitemap for category pages"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Category.objects.all().order_by('name')

    def location(self, obj):
        return reverse('products') + f'?category={obj.name}'