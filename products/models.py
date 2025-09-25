"""
Product models for Wiesbaden Cyclery
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Product category model"""
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.friendly_name or self.name

    def get_friendly_name(self):
        return self.friendly_name


class Size(models.Model):
    """Size model for products that have sizes"""
    
    name = models.CharField(max_length=10, unique=True)
    display_name = models.CharField(max_length=50)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.display_name


class Product(models.Model):
    """Product model for bicycles and accessories"""
    
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    has_sizes = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    
    # Bicycle-specific fields
    wheel_size = models.CharField(max_length=10, null=True, blank=True)
    gear_system = models.CharField(max_length=100, null=True, blank=True)
    bicycle_features = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Many-to-many relationship with sizes
    sizes = models.ManyToManyField(Size, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        """Model validation"""
        from django.core.exceptions import ValidationError
        
        # Stock validation: if in_stock is True, stock_quantity must be > 0
        if self.in_stock and (self.stock_quantity is None or self.stock_quantity <= 0):
            raise ValidationError({
                'stock_quantity': 'Stock quantity must be greater than 0 when product is in stock.'
            })
        
        # Auto-set stock_quantity to 0 when not in stock
        if not self.in_stock:
            self.stock_quantity = 0
    
    def save(self, *args, **kwargs):
        """Override save to call clean"""
        self.clean()
        super().save(*args, **kwargs)

    def get_rating_display(self):
        """Return rating as stars"""
        if self.rating:
            return '★' * int(self.rating) + '☆' * (5 - int(self.rating))
        return 'No rating'


class Review(models.Model):
    """Product review model"""
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    rating = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # One review per user per product

    def __str__(self):
        return f'{self.title} - {self.rating} stars'

    def get_rating_display(self):
        """Return rating as stars"""
        return '★' * self.rating + '☆' * (5 - self.rating)