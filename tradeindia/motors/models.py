from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

User = get_user_model()

class MotorCategory(models.Model):
    CATEGORY_CHOICES = [
        ('cars', 'Cars'),
        ('motorcycles', 'Motorcycles & Scooters'),
        ('boats', 'Boats & Marine'),
        ('trucks', 'Trucks & Commercial'),
        ('caravans', 'Caravans & Motorhomes'),
        ('parts', 'Parts & Accessories'),
        ('other', 'Other Motors')
    ]
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'display_name']
    
    def __str__(self):
        return self.display_name

class MotorMake(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(MotorCategory, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='motor_makes/', blank=True)
    
    def __str__(self):
        return self.name

class MotorModel(models.Model):
    name = models.CharField(max_length=100)
    make = models.ForeignKey(MotorMake, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.make.name} {self.name}"

class MotorListing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('as_new', 'As New'),
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged')
    ]
    
    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
        ('cng', 'CNG')
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('semi_automatic', 'Semi-Automatic')
    ]
    
    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(MotorCategory, on_delete=models.CASCADE)
    make = models.ForeignKey(MotorMake, on_delete=models.CASCADE)
    model = models.ForeignKey(MotorModel, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Vehicle Specifics
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField(help_text="Kilometers")
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    engine_size = models.FloatField(help_text="Liters", null=True, blank=True)
    doors = models.PositiveSmallIntegerField(null=True, blank=True)
    seats = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Registration & Legal
    registration_number = models.CharField(max_length=20, blank=True)
    vin_number = models.CharField(max_length=50, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)
    
    # Features (JSON field for flexibility)
    features = models.JSONField(default=dict, blank=True)
    safety_features = models.JSONField(default=list, blank=True)
    
    # Location
    location = gis_models.PointField()
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    
    # Contact
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)
    contact_preference = models.CharField(
        max_length=20, 
        choices=[('phone', 'Phone'), ('email', 'Email'), ('both', 'Both')],
        default='both'
    )
    
    # Status & Verification
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('sold', 'Sold'),
            ('reserved', 'Reserved'),
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
            models.Index(fields=['category', 'make', 'status']),
            models.Index(fields=['price', 'year']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.year} {self.make.name} {self.model.name}"

class MotorImage(models.Model):
    listing = models.ForeignKey(MotorListing, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to='motors/images/',
        processors=[ResizeToFit(1200, 800)],
        format='JPEG',
        options={'quality': 85}
    )
    thumbnail = ProcessedImageField(
        upload_to='motors/thumbnails/',
        processors=[ResizeToFit(300, 200)],
        format='JPEG',
        options={'quality': 70}
    )
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']

class MotorInquiry(models.Model):
    listing = models.ForeignKey(MotorListing, on_delete=models.CASCADE)
    inquirer = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True)
    preferred_contact = models.CharField(max_length=20, default='email')
    created_at = models.DateTimeField(auto_now_add=True)
    is_responded = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['listing', 'inquirer']