from django import forms

from .models import Address


class AddressCreateForm(forms.Form):
    
    country = forms.CharField(max_length=120)
    city = forms.CharField(max_length=120)
    line = forms.CharField(max_length=280)
