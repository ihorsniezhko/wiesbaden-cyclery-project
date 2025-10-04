import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django_countries.fields import CountryField
from products.models import Product, Size


class Order(models.Model):
    """
    Order model for managing customer orders
    """
    
    # Order Status Choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Core order information
    order_number = models.CharField(max_length=32, null=False, editable=False, unique=True)
    user_profile = models.ForeignKey(
        'accounts.UserProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders'
    )
    
    # Customer information
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Delivery information
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    
    # Order totals
    order_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=False, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    delivery_cost = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=False, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    grand_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=False, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Order status and tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Timestamps
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    # Payment information
    original_cart = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=True, blank=True, default='')
    payment_intent_id = models.CharField(max_length=254, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    # Additional order information
    order_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(
            models.Sum('lineitem_total')
        )['lineitem_total__sum'] or 0
        
        # Calculate delivery cost - free delivery over €50
        if self.order_total >= Decimal('50.00'):
            self.delivery_cost = 0
        else:
            self.delivery_cost = Decimal('4.99')
            
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

    @property
    def total_items(self):
        """Calculate total number of items in order"""
        return sum(item.quantity for item in self.lineitems.all())

    def get_status_display_badge(self):
        """Return Bootstrap badge class for order status"""
        status_badges = {
            'pending': 'badge-warning',
            'processing': 'badge-info',
            'shipped': 'badge-primary',
            'delivered': 'badge-success',
            'cancelled': 'badge-danger',
        }
        return status_badges.get(self.status, 'badge-secondary')


class OrderLineItem(models.Model):
    """
    Individual line item in an order
    """
    order = models.ForeignKey(
        Order, 
        null=False, 
        blank=False, 
        on_delete=models.CASCADE, 
        related_name='lineitems'
    )
    product = models.ForeignKey(
        Product, 
        null=False, 
        blank=False, 
        on_delete=models.CASCADE
    )
    size = models.ForeignKey(
        Size, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        null=False, 
        blank=False, 
        default=0,
        validators=[MinValueValidator(1)]
    )
    lineitem_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=False, 
        blank=False, 
        editable=False
    )

    class Meta:
        verbose_name = 'Order Line Item'
        verbose_name_plural = 'Order Line Items'

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        size_info = f" ({self.size.display_name})" if self.size else ""
        return f'SKU {self.product.sku} on order {self.order.order_number}{size_info}'


# Signal to update order total when line items are saved/deleted
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()


class OrderStatusHistory(models.Model):
    """
    Track order status changes for audit trail
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    changed_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-changed_date']
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'

    def __str__(self):
        return f'{self.order.order_number} - {self.get_status_display()} on {self.changed_date}'