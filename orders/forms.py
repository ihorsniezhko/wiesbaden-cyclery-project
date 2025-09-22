from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Order


class OrderForm(forms.ModelForm):
    """
    Form for collecting order information during checkout
    """
    
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county')

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False

    def clean_email(self):
        """Validate email field"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email

    def clean_full_name(self):
        """Validate full name field"""
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            full_name = full_name.strip()
            if len(full_name.split()) < 2:
                raise forms.ValidationError("Please enter your full name (first and last name).")
        return full_name

    def clean_phone_number(self):
        """Validate phone number field"""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove any non-digit characters except + and spaces
            import re
            phone_number = re.sub(r'[^\d\+\s\-\(\)]', '', phone_number)
            phone_number = phone_number.strip()
        return phone_number


class OrderStatusForm(forms.ModelForm):
    """
    Form for updating order status (admin use)
    """
    
    class Meta:
        model = Order
        fields = ('status',)
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }


class OrderSearchForm(forms.Form):
    """
    Form for searching orders
    """
    
    STATUS_CHOICES = [('', 'All Statuses')] + Order.STATUS_CHOICES
    
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by order number, name, or email...',
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )