from django import forms
from .models import Address
from django.contrib.auth.models import User


class AddressForm(forms.ModelForm):
    ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
    )
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'first_name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'last_name'}))
    mobile = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mobile'}))
    street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'street'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'city'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'state'}))
    zip_code = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'zip_code'}))
    
    class Meta:
        model = Address
        fields = ("first_name", "last_name", "mobile", "street", "city", "state", "zip_code",)
        