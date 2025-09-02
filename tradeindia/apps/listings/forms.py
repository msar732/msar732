"""
Forms for listings app
"""
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Row, Column, Submit, HTML, Div
from crispy_forms.bootstrap import PrependedText, AppendedText, FormActions
from .models import Listing, ListingImage, ListingReport
from apps.core.models import Category, State, District, City
import magic


class ListingForm(forms.ModelForm):
    """Form for creating/updating listings"""
    
    tags = forms.CharField(
        required=False,
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. electronics, mobile, smartphone',
            'data-role': 'tagsinput'
        })
    )
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'short_description',
            'category', 'subcategory', 'listing_type', 'condition',
            'price', 'original_price', 'is_negotiable',
            'state', 'district', 'city', 'locality', 'pin_code',
            'show_phone', 'show_email', 'allow_messages', 'whatsapp_enabled',
            'contact_name', 'contact_phone', 'contact_email',
            'tags'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter a clear and descriptive title',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your item in detail...',
                'rows': 6
            }),
            'short_description': forms.TextInput(attrs={
                'placeholder': 'Brief description (optional)',
                'maxlength': 500
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Enter price in ₹',
                'min': 0
            }),
            'original_price': forms.NumberInput(attrs={
                'placeholder': 'Original price (optional)',
                'min': 0
            }),
            'locality': forms.TextInput(attrs={
                'placeholder': 'e.g. Connaught Place, Bandra'
            }),
            'pin_code': forms.TextInput(attrs={
                'placeholder': '6-digit PIN code',
                'pattern': '[0-9]{6}',
                'maxlength': 6
            }),
            'contact_phone': forms.TextInput(attrs={
                'placeholder': '+91 98765 43210'
            }),
            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'your.email@example.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make subcategory dependent on category
        self.fields['subcategory'].queryset = Category.objects.none()
        
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Category.objects.filter(
                    parent_id=category_id,
                    is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = self.instance.category.children.filter(
                is_active=True
            )
        
        # Make district dependent on state
        self.fields['district'].queryset = District.objects.none()
        
        if 'state' in self.data:
            try:
                state_code = self.data.get('state')
                self.fields['district'].queryset = District.objects.filter(
                    state__code=state_code,
                    is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.state:
            self.fields['district'].queryset = self.instance.state.districts.filter(
                is_active=True
            )
        
        # Make city dependent on district
        self.fields['city'].queryset = City.objects.none()
        
        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['city'].queryset = City.objects.filter(
                    district_id=district_id,
                    is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.district:
            self.fields['city'].queryset = self.instance.district.cities.filter(
                is_active=True
            )
        
        # Add crispy forms helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Information',
                Field('title', css_class='form-control-lg'),
                'description',
                'short_description',
                Row(
                    Column('category', css_class='form-group col-md-6'),
                    Column('subcategory', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('listing_type', css_class='form-group col-md-6'),
                    Column('condition', css_class='form-group col-md-6'),
                ),
            ),
            Fieldset(
                'Pricing',
                Row(
                    Column(
                        PrependedText('price', '₹', css_class='form-control-lg'),
                        css_class='form-group col-md-4'
                    ),
                    Column(
                        PrependedText('original_price', '₹'),
                        css_class='form-group col-md-4'
                    ),
                    Column('is_negotiable', css_class='form-group col-md-4'),
                ),
            ),
            Fieldset(
                'Location',
                Row(
                    Column('state', css_class='form-group col-md-4'),
                    Column('district', css_class='form-group col-md-4'),
                    Column('city', css_class='form-group col-md-4'),
                ),
                Row(
                    Column('locality', css_class='form-group col-md-8'),
                    Column('pin_code', css_class='form-group col-md-4'),
                ),
            ),
            Fieldset(
                'Contact Preferences',
                Row(
                    Column('show_phone', css_class='form-group col-md-3'),
                    Column('show_email', css_class='form-group col-md-3'),
                    Column('allow_messages', css_class='form-group col-md-3'),
                    Column('whatsapp_enabled', css_class='form-group col-md-3'),
                ),
                Row(
                    Column('contact_name', css_class='form-group col-md-4'),
                    Column('contact_phone', css_class='form-group col-md-4'),
                    Column('contact_email', css_class='form-group col-md-4'),
                ),
            ),
            Field('tags'),
            Div(
                id='dynamic-attributes',
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Save Listing', css_class='btn btn-primary btn-lg'),
                HTML('<a href="{% url "listings:my_listings" %}" class="btn btn-secondary">Cancel</a>')
            )
        )
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise ValidationError("Price cannot be negative")
        return price
    
    def clean_original_price(self):
        original_price = self.cleaned_data.get('original_price')
        price = self.cleaned_data.get('price')
        
        if original_price and price and original_price < price:
            raise ValidationError("Original price should be higher than current price")
        
        return original_price
    
    def clean_pin_code(self):
        pin_code = self.cleaned_data.get('pin_code')
        if pin_code and not pin_code.isdigit():
            raise ValidationError("PIN code should contain only digits")
        if pin_code and len(pin_code) != 6:
            raise ValidationError("PIN code should be 6 digits")
        return pin_code
    
    def save(self, commit=True):
        listing = super().save(commit=False)
        
        # Handle tags
        if commit:
            listing.save()
            
            # Clear existing tags
            listing.tags.clear()
            
            # Add new tags
            tags_str = self.cleaned_data.get('tags', '')
            if tags_str:
                tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                for tag_name in tag_names:
                    listing.tags.add(tag_name)
        
        return listing


class ListingImageForm(forms.ModelForm):
    """Form for listing images"""
    
    class Meta:
        model = ListingImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'caption': forms.TextInput(attrs={
                'placeholder': 'Image caption (optional)',
                'class': 'form-control form-control-sm'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image file too large (max 10MB)")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            file_mime = magic.from_buffer(image.read(1024), mime=True)
            image.seek(0)  # Reset file pointer
            
            if file_mime not in allowed_types:
                raise ValidationError("Invalid image format. Allowed: JPEG, PNG, WebP")
        
        return image


# Inline formset for listing images
ListingImageFormSet = inlineformset_factory(
    Listing,
    ListingImage,
    form=ListingImageForm,
    extra=5,
    max_num=10,
    can_delete=True
)


class ListingReportForm(forms.ModelForm):
    """Form for reporting listings"""
    
    class Meta:
        model = ListingReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Please provide more details about your report...',
                'rows': 4,
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = True
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) < 20:
            raise ValidationError("Please provide more details (at least 20 characters)")
        return description


class ListingSearchForm(forms.Form):
    """Advanced search form for listings"""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search listings...',
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True, level=0),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    state = forms.ChoiceField(
        choices=[('', 'All States')] + list(State.objects.filter(is_active=True).values_list('code', 'name')),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min Price',
            'class': 'form-control',
            'min': 0
        })
    )
    
    price_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max Price',
            'class': 'form-control',
            'min': 0
        })
    )
    
    listing_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Listing.LISTING_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    condition = forms.ChoiceField(
        choices=[('', 'Any Condition')] + list(Listing.CONDITION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('-created_at', 'Latest First'),
            ('created_at', 'Oldest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('popular', 'Most Popular'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )