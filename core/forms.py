from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class CheckoutForm(forms.Form):
    """Form for the checkout

    """
    forename = forms.CharField(required=True)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=False)
    shipping_address = forms.CharField(required=True)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_zip = forms.CharField(required=True)
