from django import forms
from .models import Listing


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class ListingForm(forms.ModelForm):
    images = forms.FileField(widget=MultiFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Listing
        fields = ['title', 'description', 'category', 'price', 'state', 'district', 'address', 'is_active']

