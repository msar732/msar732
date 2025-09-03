"""
Trade India Hub - Unified Django Application
A comprehensive marketplace platform for motors, property, jobs, and general listings.
"""

import os
import uuid
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta

# Django imports
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg
from django.views.generic import TemplateView
from django import forms

# Third-party imports
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

# Celery imports
from celery import shared_task

# Logger setup
logger = logging.getLogger(__name__)


# ============================================================================
# USER MODELS
# ============================================================================

class CustomUser(AbstractUser):
    """Extended user model with additional fields"""
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    location = gis_models.PointField(null=True, blank=True)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trust_score = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'custom_users'
        indexes = [
            models.Index(fields=['state', 'district']),
            models.Index(fields=['trust_score']),
        ]


class UserProfile(models.Model):
    """User profile with additional information"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_categories = models.ManyToManyField('Category', blank=True)
    notification_preferences = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


# ============================================================================
# CORE MODELS
# ============================================================================

class Category(models.Model):
    """Main category model for all listings"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        indexes = [models.Index(fields=['slug', 'is_active'])]
    
    def __str__(self):
        return self.name


class State(models.Model):
    """Indian states"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
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


# ============================================================================
# LISTING MODELS
# ============================================================================

class Listing(models.Model):
    """Base listing model"""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
        ('draft', 'Draft'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = gis_models.PointField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)
    is_negotiable = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    ai_genuineness_score = models.FloatField(default=0.0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'state', 'status']),
            models.Index(fields=['price', 'created_at']),
            models.Index(fields=['ai_genuineness_score']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return self.title


class ListingImage(models.Model):
    """Images for listings"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(
        upload_to='listings/',
        processors=[ResizeToFit(800, 600)],
        format='JPEG',
        options={'quality': 80}
    )
    thumbnail = ProcessedImageField(
        upload_to='listings/thumbnails/',
        processors=[ResizeToFit(200, 150)],
        format='JPEG',
        options={'quality': 60}
    )
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['listing', 'order']


class Favorite(models.Model):
    """User favorites"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'listing']


# ============================================================================
# MOTOR MODELS
# ============================================================================

class MotorCategory(models.Model):
    """Motor categories"""
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
    """Motor manufacturers"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(MotorCategory, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='motor_makes/', blank=True)
    
    def __str__(self):
        return self.name


class MotorModel(models.Model):
    """Motor models"""
    name = models.CharField(max_length=100)
    make = models.ForeignKey(MotorMake, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.make.name} {self.name}"


class MotorListing(models.Model):
    """Motor listings"""
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
    
    # Features
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
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['listing', 'inquirer']


# ============================================================================
# PROPERTY MODELS
# ============================================================================

class PropertyListing(models.Model):
    """Property listings"""
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'Independent House'),
        ('villa', 'Villa'),
        ('plot', 'Plot/Land'),
        ('commercial', 'Commercial'),
        ('pg', 'PG/Hostel')
    ]
    
    LISTING_TYPE_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('lease', 'For Lease')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Property Details
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    area_sqft = models.PositiveIntegerField()
    floor_number = models.PositiveSmallIntegerField(null=True, blank=True)
    total_floors = models.PositiveSmallIntegerField(null=True, blank=True)
    age_years = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Amenities
    amenities = models.JSONField(default=list, blank=True)
    parking_spaces = models.PositiveSmallIntegerField(default=0)
    
    # Location
    location = gis_models.PointField()
    address = models.TextField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    pincode = models.CharField(max_length=6)
    
    # Contact
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=Listing.STATUS_CHOICES, default='active')
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
    
    def __str__(self):
        return self.title


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


# ============================================================================
# JOB MODELS
# ============================================================================

class JobCategory(models.Model):
    """Job categories"""
    CATEGORY_CHOICES = [
        ('it', 'Information Technology'),
        ('finance', 'Finance & Banking'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('sales', 'Sales & Marketing'),
        ('engineering', 'Engineering'),
        ('hospitality', 'Hospitality'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('other', 'Other')
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
        ('freelance', 'Freelance'),
        ('internship', 'Internship')
    ]
    
    EXPERIENCE_CHOICES = [
        ('fresher', '0-1 years'),
        ('junior', '1-3 years'),
        ('mid', '3-7 years'),
        ('senior', '7-12 years'),
        ('expert', '12+ years')
    ]
    
    SALARY_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('annually', 'Annually'),
        ('hourly', 'Hourly'),
        ('project', 'Per Project')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    
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
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)
    
    # Application details
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
            ('draft', 'Draft')
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
    
    def __str__(self):
        return self.job_title


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


# ============================================================================
# AI VERIFICATION MODELS
# ============================================================================

class AIVerificationResult(models.Model):
    """AI verification results for listings"""
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE)
    genuineness_score = models.FloatField()
    text_analysis_score = models.FloatField()
    image_analysis_score = models.FloatField()
    location_verification_score = models.FloatField()
    is_genuine = models.BooleanField()
    verification_details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Verification for {self.listing.title} - Score: {self.genuineness_score}"


# ============================================================================
# AI/ML CLASSES
# ============================================================================

class MotorPricePredictor:
    """AI model for motor price prediction and analysis"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            model_path = os.path.join('ai_models', 'motor_price_model.pkl')
            self.model = joblib.load(model_path)
            
            vectorizer_path = os.path.join('ai_models', 'motor_text_vectorizer.pkl')
            self.vectorizer = joblib.load(vectorizer_path)
        except:
            # Initialize new models if not found
            self.initialize_models()
    
    def initialize_models(self):
        """Initialize new ML models"""
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=1000)
    
    def analyze_listing(self, listing):
        """Analyze motor listing for price prediction"""
        features = self.extract_features(listing)
        
        try:
            predicted_price = self.model.predict([features])[0]
            market_position = self.determine_market_position(listing.price, predicted_price)
            
            return {
                'predicted_price': round(predicted_price, 2),
                'market_position': market_position,
                'price_trend': self.get_price_trend(listing),
                'similar_avg': self.get_similar_listings_avg(listing)
            }
        except:
            return {
                'predicted_price': float(listing.price),
                'market_position': 'average',
                'price_trend': 'stable',
                'similar_avg': float(listing.price)
            }
    
    def extract_features(self, listing):
        """Extract numerical features from listing"""
        return [
            listing.year,
            listing.mileage,
            listing.engine_size or 1.0,
            len(listing.title.split()),
            1 if listing.fuel_type == 'petrol' else 0,
            1 if listing.transmission == 'automatic' else 0,
            listing.doors or 4,
            listing.condition == 'excellent'
        ]
    
    def determine_market_position(self, actual_price, predicted_price):
        """Determine if price is above/below market"""
        ratio = float(actual_price) / predicted_price
        if ratio > 1.15:
            return 'above_market'
        elif ratio < 0.85:
            return 'below_market'
        return 'market_average'
    
    def get_price_trend(self, listing):
        """Get price trend for similar vehicles"""
        return 'stable'  # Simplified for demo
    
    def get_similar_listings_avg(self, listing):
        """Get average price of similar listings"""
        similar = MotorListing.objects.filter(
            make=listing.make,
            year__range=(listing.year-2, listing.year+2),
            status='active'
        ).exclude(id=listing.id)
        
        if similar.exists():
            return float(similar.aggregate(avg_price=Avg('price'))['avg_price'] or listing.price)
        return float(listing.price)


class RecommendationEngine:
    """AI-powered recommendation system"""
    
    def __init__(self):
        self.user_item_matrix = None
        self.similarity_matrix = None
    
    def get_user_recommendations(self, user, limit=10):
        """Get personalized recommendations for user"""
        cache_key = f'recommendations_user_{user.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Get user's viewing and favoriting history
        user_interactions = self.get_user_interactions(user)
        
        # Content-based recommendations
        content_recs = self.content_based_recommendations(user_interactions, limit//2)
        
        # Collaborative filtering recommendations
        collab_recs = self.collaborative_recommendations(user, limit//2)
        
        # Combine and deduplicate
        recommendations = list(set(content_recs + collab_recs))[:limit]
        
        # Cache for 1 hour
        cache.set(cache_key, recommendations, 3600)
        return recommendations
    
    def get_user_interactions(self, user):
        """Get user's interaction history"""
        # Get user's favorites and recent views
        favorites = Favorite.objects.filter(user=user).values_list('listing_id', flat=True)
        
        return {
            'categories': ['motors', 'electronics'],
            'price_range': (50000, 500000),
            'locations': [user.state, user.district]
        }
    
    def content_based_recommendations(self, user_interactions, limit):
        """Content-based filtering"""
        recommendations = Listing.objects.filter(
            status='active',
            price__range=(
                user_interactions.get('price_range', (0, 1000000))[0],
                user_interactions.get('price_range', (0, 1000000))[1]
            )
        ).order_by('-ai_genuineness_score', '-created_at')[:limit]
        
        return list(recommendations)
    
    def collaborative_recommendations(self, user, limit):
        """Collaborative filtering recommendations"""
        similar_users = self.find_similar_users(user)
        
        recommendations = Listing.objects.filter(
            status='active'
        ).order_by('-view_count')[:limit]
        
        return list(recommendations)
    
    def find_similar_users(self, user):
        """Find users with similar preferences"""
        return CustomUser.objects.filter(
            state=user.state
        ).exclude(id=user.id)[:10]


# ============================================================================
# DJANGO VIEWS
# ============================================================================

class HomeView(TemplateView):
    """Main homepage view"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured listings from all categories
        context['featured_motors'] = MotorListing.objects.filter(
            is_featured=True, status='active'
        )[:6]
        
        context['featured_properties'] = PropertyListing.objects.filter(
            is_featured=True, status='active'
        )[:6]
        
        context['featured_jobs'] = JobListing.objects.filter(
            is_featured=True, status='active'
        )[:6]
        
        # Statistics
        context['stats'] = {
            'total_listings': Listing.objects.filter(status='active').count(),
            'total_users': CustomUser.objects.count(),
            'verified_listings': Listing.objects.filter(is_verified=True).count(),
        }
        
        return context


def motors_home(request):
    """Motors marketplace homepage"""
    categories = MotorCategory.objects.filter(is_active=True)
    featured_listings = MotorListing.objects.filter(
        is_featured=True, status='active'
    )[:12]
    
    # Popular makes with listing counts
    popular_makes = MotorMake.objects.annotate(
        listing_count=Count('motormodel__motorlisting')
    ).order_by('-listing_count')[:10]
    
    context = {
        'categories': categories,
        'featured_listings': featured_listings,
        'popular_makes': popular_makes,
    }
    
    return render(request, 'motors/home.html', context)


def motor_detail(request, listing_id):
    """Detailed motor listing view"""
    listing = get_object_or_404(
        MotorListing.objects.select_related('user', 'make', 'model')
        .prefetch_related('images'), 
        id=listing_id
    )
    
    # Increment view count
    listing.view_count += 1
    listing.save(update_fields=['view_count'])
    
    # Similar listings
    similar_listings = MotorListing.objects.filter(
        make=listing.make,
        status='active'
    ).exclude(id=listing.id)[:6]
    
    # Price analysis using AI
    price_analysis = get_ai_price_analysis(listing)
    
    context = {
        'listing': listing,
        'similar_listings': similar_listings,
        'price_analysis': price_analysis,
    }
    
    return render(request, 'motors/detail.html', context)


@login_required
def create_motor_listing(request):
    """Create new motor listing"""
    if request.method == 'POST':
        form = MotorListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                MotorImage.objects.create(
                    listing=listing,
                    image=image,
                    order=i,
                    is_primary=(i == 0)
                )
            
            # Trigger AI verification
            verify_motor_listing.delay(listing.id)
            
            return redirect('motors:detail', listing_id=listing.id)
    else:
        form = MotorListingForm()
    
    context = {
        'form': form,
        'categories': MotorCategory.objects.filter(is_active=True),
    }
    
    return render(request, 'motors/create.html', context)


# ============================================================================
# DJANGO FORMS
# ============================================================================

class MotorListingForm(forms.ModelForm):
    """Form for creating motor listings"""
    class Meta:
        model = MotorListing
        fields = [
            'category', 'make', 'model', 'title', 'description', 'price',
            'condition', 'year', 'mileage', 'fuel_type', 'transmission',
            'engine_size', 'doors', 'seats', 'registration_number',
            'address', 'contact_phone', 'contact_email', 'is_negotiable'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class MotorInquiryForm(forms.ModelForm):
    """Form for motor inquiries"""
    class Meta:
        model = MotorInquiry
        fields = ['message', 'phone_number']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your inquiry message...'}),
        }


class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'state', 'district']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


# ============================================================================
# AI VERIFICATION TASKS
# ============================================================================

@shared_task
def verify_listing_genuineness(listing_id):
    """AI task to verify listing genuineness"""
    try:
        listing = Listing.objects.get(pk=listing_id)
        
        # Text analysis score
        text_score = analyze_text_genuineness(listing.title, listing.description)
        
        # Image analysis score
        image_score = analyze_images_genuineness(listing.images.all())
        
        # Location verification score
        location_score = verify_location_consistency(listing)
        
        # Calculate overall genuineness score
        overall_score = (text_score * 0.4 + image_score * 0.4 + location_score * 0.2)
        
        # Update listing
        listing.ai_genuineness_score = overall_score
        listing.is_verified = overall_score > 0.7
        listing.save()
        
        # Create verification result
        AIVerificationResult.objects.update_or_create(
            listing=listing,
            defaults={
                'genuineness_score': overall_score,
                'text_analysis_score': text_score,
                'image_analysis_score': image_score,
                'location_verification_score': location_score,
                'is_genuine': overall_score > 0.7,
                'verification_details': {
                    'text_indicators': get_text_indicators(listing.title, listing.description),
                    'image_indicators': get_image_indicators(listing.images.all()),
                    'location_indicators': get_location_indicators(listing)
                }
            }
        )
        
        logger.info(f"Verified listing {listing_id} with score {overall_score}")
        return overall_score
        
    except Exception as e:
        logger.error(f"Error verifying listing {listing_id}: {str(e)}")
        return 0.0


def analyze_text_genuineness(title, description):
    """Analyze text for genuineness indicators"""
    spam_indicators = [
        'urgent', 'limited time', 'act now', 'guaranteed',
        'free money', 'click here', 'call now'
    ]
    
    text = (title + " " + description).lower()
    spam_count = sum(1 for indicator in spam_indicators if indicator in text)
    
    # Calculate base score
    base_score = 1.0 - (spam_count * 0.2)
    
    # Additional checks
    if len(description) < 20:
        base_score -= 0.2
    if title.isupper():
        base_score -= 0.1
    
    return max(0.0, min(1.0, base_score))


def analyze_images_genuineness(images):
    """Analyze images for genuineness"""
    if not images.exists():
        return 0.3
    
    # Simple heuristic: more images = more genuine
    image_count = images.count()
    base_score = min(1.0, image_count * 0.2)
    
    # Check for multiple images
    if image_count >= 3:
        base_score += 0.2
    
    return min(1.0, base_score)


def verify_location_consistency(listing):
    """Verify location consistency"""
    try:
        # Check if district belongs to state
        if hasattr(listing.district, 'state') and listing.district.state != listing.state:
            return 0.0
        return 0.8
    except:
        return 0.5


def get_text_indicators(title, description):
    """Get text analysis indicators"""
    return {
        'title_length': len(title),
        'description_length': len(description),
        'has_contact_info': any(word in description.lower() for word in ['phone', 'email', 'contact'])
    }


def get_image_indicators(images):
    """Get image analysis indicators"""
    return {
        'image_count': images.count(),
        'has_primary': images.filter(is_primary=True).exists()
    }


def get_location_indicators(listing):
    """Get location analysis indicators"""
    return {
        'has_address': bool(listing.address)
    }


def get_ai_price_analysis(listing):
    """Get AI price analysis for a listing"""
    try:
        predictor = MotorPricePredictor()
        return predictor.analyze_listing(listing)
    except Exception as e:
        logger.error(f"Error in AI price analysis: {str(e)}")
        return {
            'predicted_price': float(listing.price),
            'market_position': 'average',
            'price_trend': 'stable',
            'similar_avg': float(listing.price)
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_cache_key(prefix, *args):
    """Generate cache key"""
    import hashlib
    key_string = f"{prefix}_{'_'.join(map(str, args))}"
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_listing_data(listing_id, data, timeout=300):
    """Cache listing data"""
    cache_key = get_cache_key('listing', listing_id)
    cache.set(cache_key, data, timeout)


def get_cached_listing_data(listing_id):
    """Get cached listing data"""
    cache_key = get_cache_key('listing', listing_id)
    return cache.get(cache_key)


# ============================================================================
# API VIEWS
# ============================================================================

def health_check(request):
    """System health check endpoint"""
    try:
        # Check database
        db_status = check_database()
        
        # Check cache
        cache_status = check_cache()
        
        overall_status = 'healthy' if db_status and cache_status else 'unhealthy'
        
        return JsonResponse({
            'status': overall_status,
            'database': 'ok' if db_status else 'error',
            'cache': 'ok' if cache_status else 'error',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)


def check_database():
    """Check database connectivity"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except:
        return False


def check_cache():
    """Check cache connectivity"""
    try:
        cache.set('health_check', 'ok', 60)
        return cache.get('health_check') == 'ok'
    except:
        return False


# ============================================================================
# SEARCH FUNCTIONALITY
# ============================================================================

def search_suggestions(request):
    """Get search suggestions"""
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search in titles
    suggestions = []
    
    # Motor suggestions
    motor_suggestions = MotorListing.objects.filter(
        Q(title__icontains=query) | Q(make__name__icontains=query),
        status='active'
    ).values_list('title', flat=True)[:5]
    
    suggestions.extend(list(motor_suggestions))
    
    # Property suggestions
    property_suggestions = PropertyListing.objects.filter(
        Q(title__icontains=query),
        status='active'
    ).values_list('title', flat=True)[:5]
    
    suggestions.extend(list(property_suggestions))
    
    return JsonResponse({
        'suggestions': list(set(suggestions))[:10]
    })


# ============================================================================
# MAIN APPLICATION SETUP
# ============================================================================

# Set User model reference
User = CustomUser

# Initialize AI components
motor_price_predictor = MotorPricePredictor()
recommendation_engine = RecommendationEngine()

# Application metadata
APP_NAME = "Trade India Hub"
VERSION = "1.0.0"
DESCRIPTION = "Comprehensive marketplace platform for India"

if __name__ == "__main__":
    print(f"{APP_NAME} v{VERSION}")
    print(f"Description: {DESCRIPTION}")
    print("This file contains all the core models, views, and AI functionality.")