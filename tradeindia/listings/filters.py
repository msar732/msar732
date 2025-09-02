import django_filters
from django import forms
from .models import Listing, Category
from locations.models import State, District, City


class ListingFilter(django_filters.FilterSet):
    """Filter class for advanced listing search"""
    
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search by title...', 'class': 'form-control'})
    )
    
    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search in description...', 'class': 'form-control'})
    )
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    state = django_filters.ModelChoiceFilter(
        queryset=State.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'state-select'})
    )
    
    district = django_filters.ModelChoiceFilter(
        queryset=District.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'district-select'})
    )
    
    city = django_filters.ModelChoiceFilter(
        queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'city-select'})
    )
    
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        widget=forms.NumberInput(attrs={'placeholder': 'Min price', 'class': 'form-control'})
    )
    
    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        widget=forms.NumberInput(attrs={'placeholder': 'Max price', 'class': 'form-control'})
    )
    
    listing_type = django_filters.ChoiceFilter(
        choices=Listing.LISTING_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_negotiable = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_featured = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_urgent = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    created_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'class': 'form-control'})
    )
    
    tags = django_filters.CharFilter(
        field_name='tags',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search by tags...', 'class': 'form-control'})
    )
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'category', 'state', 'district', 'city',
            'min_price', 'max_price', 'listing_type', 'is_negotiable',
            'is_featured', 'is_urgent', 'created_at', 'tags'
        ]