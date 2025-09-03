# Trade India - Complete Marketplace Application
# Fixed and organized code with proper structure

import os
import sys
import django
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradeindia.settings')
django.setup()

# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.contrib.auth import get_user_model

# =============================================================================
# CORE MODELS
# =============================================================================

class CustomUser(AbstractUser):
    """Extended user model with additional fields"""
    phone_number = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = gis_models.PointField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    
    # Trust and verification
    trust_score = models.FloatField(default=5.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(default=list, blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

class State(models.Model):
    """Indian states"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    
    def __str__(self):
        return self.name

class District(models.Model):
    """Indian districts"""
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    
    class Meta:
        unique_together = ['name', 'state']
    
    def __str__(self):
        return f"{self.name}, {self.state.name}"

class Category(models.Model):
    """Listing categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

# =============================================================================
# LISTINGS MODELS
# =============================================================================

class Listing(models.Model):
    """Base listing model"""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('draft', 'Draft')
    ]
    
    # Basic Information
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Location
    location = gis_models.PointField()
    address = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    
    # Contact Information
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)
    
    # Status & Features
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_negotiable = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    ai_genuineness_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    
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
            models.Index(fields=['category', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return self.title

class ListingImage(models.Model):
    """Listing images"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to='listings/images/',
        processors=[ResizeToFit(1200, 800)],
        format='JPEG',
        options={'quality': 85}
    )
    thumbnail = ProcessedImageField(
        upload_to='listings/thumbnails/',
        processors=[ResizeToFit(300, 200)],
        format='JPEG',
        options={'quality': 70}
    )
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']

class Favorite(models.Model):
    """User favorites"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'listing']

# =============================================================================
# MOTORS MODELS
# =============================================================================

class MotorCategory(models.Model):
    """Motor vehicle categories"""
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
        verbose_name_plural = "Motor Categories"
    
    def __str__(self):
        return self.display_name

class MotorMake(models.Model):
    """Motor vehicle makes"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(MotorCategory, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='motor_makes/', blank=True)
    
    class Meta:
        unique_together = ['name', 'category']
    
    def __str__(self):
        return self.name

class MotorModel(models.Model):
    """Motor vehicle models"""
    name = models.CharField(max_length=100)
    make = models.ForeignKey(MotorMake, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['name', 'make']
    
    def __str__(self):
        return f"{self.make.name} {self.name}"

class MotorListing(models.Model):
    """Motor vehicle listings"""
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(MotorCategory, on_delete=models.CASCADE)
    make = models.ForeignKey(MotorMake, on_delete=models.CASCADE)
    model = models.ForeignKey(MotorModel, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Vehicle Specifics
    year = models.PositiveIntegerField(validators=[MinValueValidator(1980), MaxValueValidator(2025)])
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
    
    # Features
    features = models.JSONField(default=dict, blank=True)
    safety_features = models.JSONField(default=list, blank=True)
    
    # Location
    location = gis_models.PointField()
    address = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    
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
    ai_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    
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
    """Motor listing images"""
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
    """Motor inquiries"""
    listing = models.ForeignKey(MotorListing, on_delete=models.CASCADE)
    inquirer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True)
    preferred_contact = models.CharField(max_length=20, default='email')
    created_at = models.DateTimeField(auto_now_add=True)
    is_responded = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['listing', 'inquirer']

# =============================================================================
# PROPERTY MODELS
# =============================================================================

class PropertyType(models.Model):
    """Property types"""
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
    """Property listings"""
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
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
    
    # Amenities
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
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
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
    ai_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    
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
    """Property listing images"""
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
    property = models.ForeignKey(PropertyListing, on_delete=models.CASCADE)
    inquirer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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

# =============================================================================
# JOBS MODELS
# =============================================================================

class JobCategory(models.Model):
    """Job categories"""
    CATEGORY_CHOICES = [
        ('it_software', 'IT & Software'),
        ('marketing_sales', 'Marketing & Sales'),
        ('finance_accounting', 'Finance & Accounting'),
        ('engineering', 'Engineering'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education & Training'),
        ('hospitality', 'Hospitality & Tourism'),
        ('construction', 'Construction'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('government', 'Government Jobs'),
        ('freelance', 'Freelance & Part-time'),
        ('other', 'Other Jobs')
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name

class Company(models.Model):
    """Company profiles for job listings"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='companies/', blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    size = models.CharField(
        max_length=20,
        choices=[
            ('startup', '1-10 employees'),
            ('small', '11-50 employees'),
            ('medium', '51-200 employees'),
            ('large', '201-1000 employees'),
            ('enterprise', '1000+ employees')
        ]
    )
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=200)
    
    # Company verification
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name

class JobListing(models.Model):
    """Job listings"""
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('temporary', 'Temporary')
    ]
    
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('0_1', '0-1 years'),
        ('1_3', '1-3 years'),
        ('3_5', '3-5 years'),
        ('5_10', '5-10 years'),
        ('10_plus', '10+ years')
    ]
    
    SALARY_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('annually', 'Annually'),
        ('hourly', 'Hourly'),
        ('project', 'Per Project'),
        ('negotiable', 'Negotiable')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    
    # Job Details
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    job_description = models.TextField()
    requirements = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    
    # Experience & Education
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    education_required = models.TextField(blank=True)
    skills_required = models.JSONField(default=list, blank=True)
    
    # Salary
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES, default='monthly')
    
    # Location
    location = gis_models.PointField()
    address = models.TextField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    is_remote = models.BooleanField(default=False)
    
    # Application Details
    application_deadline = models.DateField(null=True, blank=True)
    positions_available = models.PositiveIntegerField(default=1)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('filled', 'Position Filled'),
            ('expired', 'Expired'),
            ('paused', 'Paused')
        ],
        default='active'
    )
    
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['salary_min', 'salary_max']),
        ]
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class JobApplication(models.Model):
    """Job applications"""
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    
    class Meta:
        unique_together = ['job', 'applicant']

class JobAlert(models.Model):
    """Job alerts for users"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    alert_name = models.CharField(max_length=100)
    keywords = models.CharField(max_length=500)
    categories = models.ManyToManyField(JobCategory)
    location = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    experience_level = models.CharField(max_length=20, choices=JobListing.EXPERIENCE_CHOICES, blank=True)
    job_type = models.CharField(max_length=20, choices=JobListing.JOB_TYPE_CHOICES, blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediately'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly')
        ],
        default='daily'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.alert_name}"

# =============================================================================
# AI VERIFICATION MODELS
# =============================================================================

class AIVerificationResult(models.Model):
    """AI verification results for listings"""
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='ai_verification')
    genuineness_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    text_analysis_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    image_analysis_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    location_verification_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    is_genuine = models.BooleanField(default=False)
    verification_details = models.JSONField(default=dict, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"AI Verification for {self.listing.title} - Score: {self.genuineness_score}"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_ai_recommendations(user, limit=10):
    """Get AI-powered recommendations for a user"""
    # This would integrate with actual AI/ML models
    # For now, return featured listings
    from django.db.models import Q
    
    recommendations = Listing.objects.filter(
        Q(status='active') & Q(is_featured=True)
    ).order_by('-ai_genuineness_score', '-created_at')[:limit]
    
    return recommendations

def verify_listing_genuineness(listing):
    """Verify listing genuineness using AI"""
    # This would integrate with actual AI/ML models
    # For now, return a basic score
    score = 7.5  # Default score
    
    # Basic checks
    if listing.description and len(listing.description) > 50:
        score += 0.5
    if listing.images.exists():
        score += 1.0
    if listing.contact_phone:
        score += 0.5
    
    return min(10.0, score)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("Trade India - Complete Marketplace Application")
    print("=" * 50)
    print("Models loaded successfully!")
    print(f"Total models defined: {len([m for m in globals().values() if isinstance(m, type) and issubclass(m, models.Model) and m != models.Model])}")
    print("\nAvailable models:")
    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, models.Model) and obj != models.Model:
            print(f"  - {name}")
    print("\nApplication ready to use!")