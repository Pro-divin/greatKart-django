from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'country', 'city', 'district', 'order_note']
    district = forms.CharField(required=False)  # make it optional

        