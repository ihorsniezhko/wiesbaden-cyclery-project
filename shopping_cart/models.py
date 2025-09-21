from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal
from products.models import Product, Size


class Cart(models.Model):
    """
    Shopping cart model that supports both authenticated users and anonymous sessions
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Associated user for authenticated carts"
    )
    session_key = models.CharField(
        max_length=40, 
        null=True, 
        blank=True,
        help_text="Session key for anonymous carts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous cart ({self.session_key[:8]}...)"

    @property
    def total_items(self):
        """Calculate total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Calculate cart subtotal before delivery"""
        return sum(item.line_total for item in self.items.all())

    @property
    def delivery_cost(self):
        """Calculate delivery cost - free over €50"""
        if self.subtotal >= Decimal('50.00'):
            return Decimal('0.00')
        return Decimal('4.99')

    @property
    def total(self):
        """Calculate total including delivery"""
        return self.subtotal + self.delivery_cost

    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """
    Individual item in a shopping cart
    """
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE
    )
    size = models.ForeignKey(
        Size, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Size selection for products that have sizes"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ('cart', 'product', 'size')

    def __str__(self):
        size_info = f" ({self.size})" if self.size else ""
        return f"{self.quantity}x {self.product.name}{size_info}"

    @property
    def line_total(self):
        """Calculate total for this cart item"""
        return self.product.price * self.quantity

    def clean(self):
        """Validate cart item"""
        from django.core.exceptions import ValidationError
        
        # Check if product requires size but none provided
        if self.product.sizes.exists() and not self.size:
            raise ValidationError("This product requires a size selection.")
        
        # Check if size is valid for this product
        if self.size and not self.product.sizes.filter(id=self.size.id).exists():
            raise ValidationError("Selected size is not available for this product.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)