"""
Forms for products app
"""
from django import forms
from .models import Review


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