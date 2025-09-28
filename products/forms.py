"""
Forms for products app
"""
from django import forms
from .models import Product, Review, Category, Size


class ProductForm(forms.ModelForm):
    """Comprehensive form for adding/editing products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'description', 'price', 
            'in_stock', 'stock_quantity', 'has_sizes', 'sizes',
            'wheel_size', 'gear_system', 'bicycle_features',
            'image', 'image_url', 'rating'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product SKU (optional)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': '1',
                'max': '9999',
                'placeholder': '1'
            }),

            'wheel_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 700c, 29"'
            }),
            'gear_system': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Shimano 105 22-speed'
            }),
            'bicycle_features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional bicycle features and specifications'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image URL (optional)'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sizes': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'name': 'Product Name',
            'sku': 'SKU',
            'category': 'Category',
            'description': 'Description',
            'price': 'Price (€)',
            'in_stock': 'In Stock',
            'stock_quantity': 'Stock Quantity',
            'has_sizes': 'Has Sizes',
            'sizes': 'Available Sizes',

            'wheel_size': 'Wheel Size',
            'gear_system': 'Gear System',
            'bicycle_features': 'Bicycle Features',
            'image': 'Product Image',
            'image_url': 'Image URL',
            'rating': 'Rating (1-5)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category field show friendly names
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select Category"
        
        # Make sizes field show display names
        self.fields['sizes'].queryset = Size.objects.all().order_by('sort_order')
        
        # Check if product previously had sizes - if so, disable the has_sizes checkbox
        if self.instance and self.instance.pk:
            # Check if this product previously had sizes assigned
            previously_had_sizes = self.instance.sizes.exists()
            if previously_had_sizes:
                # Disable the has_sizes field and add a help text
                self.fields['has_sizes'].disabled = True
                self.fields['has_sizes'].help_text = (
                    "This product previously had sizes assigned. "
                    "The 'Has Sizes' option cannot be disabled to maintain data integrity."
                )
                # Add a CSS class to style the disabled field
                self.fields['has_sizes'].widget.attrs.update({
                    'class': 'form-check-input disabled-field',
                    'title': 'Cannot be disabled - product previously had sizes'
                })

    def clean(self):
        """Custom validation with context-aware logic"""
        cleaned_data = super().clean()
        in_stock = cleaned_data.get('in_stock')
        stock_quantity = cleaned_data.get('stock_quantity')
        has_sizes = cleaned_data.get('has_sizes')
        sizes = cleaned_data.get('sizes')
        category = cleaned_data.get('category')
        
        # Stock validation - CRITICAL: Stock quantity must be > 0 when in stock
        if in_stock and (stock_quantity is None or stock_quantity <= 0):
            raise forms.ValidationError(
                "Stock quantity must be greater than 0 when product is marked as 'In Stock'."
            )
        
        # Auto-clear stock quantity when not in stock
        if not in_stock:
            cleaned_data['stock_quantity'] = 0
        
        # CRITICAL: Prevent disabling has_sizes if product previously had sizes
        if self.instance and self.instance.pk:
            previously_had_sizes = self.instance.sizes.exists()
            if previously_had_sizes:
                # Force has_sizes to True for products that previously had sizes
                cleaned_data['has_sizes'] = True
                # Only show error if user explicitly tried to disable it (field is not disabled)
                # When field is disabled, browser doesn't send it, so we shouldn't validate it
                if not self.fields['has_sizes'].disabled:
                    if self.data.get('has_sizes') == 'False' or not self.data.get('has_sizes'):
                        self.add_error('has_sizes', 
                            "Cannot disable 'Has Sizes' for products that previously had sizes assigned. "
                            "This maintains data integrity and prevents confusion."
                        )
        
        # Size validation
        if has_sizes and not sizes:
            raise forms.ValidationError(
                "Please select at least one size when 'Has Sizes' is enabled."
            )
        
        # Auto-clear sizes when has_sizes is False
        if not has_sizes:
            cleaned_data['sizes'] = []
        
        # Rating validation
        rating = cleaned_data.get('rating')
        if rating is not None and rating not in [1, 2, 3, 4, 5]:
            raise forms.ValidationError(
                "Rating must be an integer from 1 to 5."
            )
        
        # Category-specific validation
        bicycle_categories = ['road_bikes', 'mountain_bikes', 'electric_bikes']
        if category and category.name in bicycle_categories:
            # For bicycle categories, suggest bicycle-specific fields
            if not cleaned_data.get('wheel_size'):
                self.add_error('wheel_size', 'Consider adding wheel size for bicycle products.')
        
        return cleaned_data


class ReviewForm(forms.ModelForm):
    """Form for adding product reviews"""
    
    class Meta:
        model = Review
        fields = ['title', 'rating', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            }),
        }
        labels = {
            'title': 'Review Title',
            'rating': 'Rating',
            'comment': 'Your Review',
        }