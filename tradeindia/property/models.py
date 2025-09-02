from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

User = get_user_model()

class PropertyAmenity(models.Model):
    """Property amenities master data"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('basic', 'Basic Amenities'),
            ('security', 'Security'),
            ('recreation', 'Recreation'),
            ('convenience', 'Convenience'),
            ('transport', 'Transportation')
        ]
    )
    is_popular = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class PropertyInquiry(models.Model):
    """Property inquiry management"""
    property = models.ForeignKey('PropertyListing', on_delete=models.CASCADE)
    inquirer = models.ForeignKey(User, on_delete=models.CASCADE)
    inquiry_type = models.CharField(
        max_length=20,
        choices=[
            ('viewing', 'Schedule Viewing'),
            ('info', 'Request Info'),
            ('negotiation', 'Price Negotiation'),
            ('loan', 'Loan Assistance')
        ]
    )
    message = models.TextField()
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('contacted', 'Contacted'),
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed')
        ],
        default='pending'
    )
    
    class Meta:
        unique_together = ['property', 'inquirer']

class PropertyType(models.Model):
    PROPERTY_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('land', 'Land & Plots'),
        ('rental', 'Rentals'),
        ('pg_hostel', 'PG & Hostels'),
        ('warehouse', 'Warehouse'),
        ('office', 'Office Space'),
        ('shop', 'Shops & Showrooms')
    ]
    
    name = models.CharField(max_length=50, choices=PROPERTY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name

class PropertyListing(models.Model):
    LISTING_TYPE_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('lease', 'For Lease'),
        ('pg', 'PG/Hostel')
    ]
    
    PROPERTY_STATUS_CHOICES = [
        ('ready', 'Ready to Move'),
        ('under_construction', 'Under Construction'),
        ('new_launch', 'New Launch')
    ]
    
    FACING_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('northeast', 'North-East'),
        ('northwest', 'North-West'),
        ('southeast', 'South-East'),
        ('southwest', 'South-West')
    ]
    
    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=15, decimal_places=2)
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    maintenance_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Property Details
    carpet_area = models.PositiveIntegerField(help_text="Square feet", null=True, blank=True)
    built_up_area = models.PositiveIntegerField(help_text="Square feet", null=True, blank=True)
    plot_area = models.PositiveIntegerField(help_text="Square feet", null=True, blank=True)
    
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    balconies = models.PositiveSmallIntegerField(null=True, blank=True)
    floors_total = models.PositiveSmallIntegerField(null=True, blank=True)
    floor_number = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Property Features
    property_age = models.PositiveSmallIntegerField(help_text="Years", null=True, blank=True)
    facing = models.CharField(max_length=20, choices=FACING_CHOICES, blank=True)
    furnishing = models.CharField(
        max_length=20,
        choices=[
            ('unfurnished', 'Unfurnished'),
            ('semi_furnished', 'Semi Furnished'),
            ('fully_furnished', 'Fully Furnished')
        ],
        blank=True
    )
    
    # Amenities (JSON field for flexibility)
    amenities = models.JSONField(default=list, blank=True)
    parking = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Parking'),
            ('bike', 'Bike Parking'),
            ('car', 'Car Parking'),
            ('both', 'Both')
        ],
        default='none'
    )
    
    # Location
    location = gis_models.PointField()
    address = models.TextField()
    locality = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Legal & Documentation
    property_status = models.CharField(max_length=30, choices=PROPERTY_STATUS_CHOICES, default='ready')
    possession_date = models.DateField(null=True, blank=True)
    property_id = models.CharField(max_length=50, blank=True)
    rera_id = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)
    
    # Status & Verification
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('sold', 'Sold'),
            ('rented', 'Rented'),
            ('expired', 'Expired')
        ],
        default='active'
    )
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    ai_score = models.FloatField(default=0.0)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    inquiry_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_type', 'listing_type', 'status']),
            models.Index(fields=['price', 'carpet_area']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_listing_type_display()}"

class PropertyImage(models.Model):
    listing = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to='property/images/',
        processors=[ResizeToFit(1200, 800)],
        format='JPEG',
        options={'quality': 85}
    )
    thumbnail = ProcessedImageField(
        upload_to='property/thumbnails/',
        processors=[ResizeToFit(300, 200)],
        format='JPEG',
        options={'quality': 70}
    )
    room_type = models.CharField(
        max_length=50,
        choices=[
            ('exterior', 'Exterior'),
            ('living_room', 'Living Room'),
            ('bedroom', 'Bedroom'),
            ('kitchen', 'Kitchen'),
            ('bathroom', 'Bathroom'),
            ('balcony', 'Balcony'),
            ('other', 'Other')
        ],
        default='other'
    )
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']