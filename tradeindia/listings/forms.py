from django import forms
from .models import Listing, ListingImage, Category, State, District

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'category', 'title', 'description', 'price', 'condition',
            'state', 'district', 'address', 'contact_phone', 'contact_email',
            'is_negotiable'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ListingImageForm(forms.ModelForm):
    class Meta:
        model = ListingImage
        fields = ['image', 'alt_text']