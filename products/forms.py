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
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '5'
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
            'rating': 'Rating (0-5)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category field show friendly names
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select Category"
        
        # Make sizes field show display names
        self.fields['sizes'].queryset = Size.objects.all().order_by('sort_order')

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
        
        # Size validation
        if has_sizes and not sizes:
            raise forms.ValidationError(
                "Please select at least one size when 'Has Sizes' is enabled."
            )
        
        # Auto-clear sizes when has_sizes is False
        if not has_sizes:
            cleaned_data['sizes'] = []
        
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