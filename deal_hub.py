# AI-powered recommendation system - ai_verification/ml_models.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache
from django.db import models
from django.contrib.auth import get_user_model
import joblib
import os

# Get User model
User = get_user_model()

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
        # Simplified trend analysis
        return 'stable'  # In real implementation, analyze historical data
    
    def get_similar_listings_avg(self, listing):
        """Get average price of similar listings"""
        from motors.models import MotorListing
        
        similar = MotorListing.objects.filter(
            make=listing.make,
            year__range=(listing.year-2, listing.year+2),
            status='active'
        ).exclude(id=listing.id)
        
        if similar.exists():
            return float(similar.aggregate(avg_price=models.Avg('price'))['avg_price'] or listing.price)
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
        from listings.models import Listing, Favorite
        from motors.models import MotorListing
        
        # Get user's favorites and recent views
        favorites = Favorite.objects.filter(user=user).values_list('listing_id', flat=True)
        
        # For demo, return some sample interactions
        return {
            'categories': ['motors', 'electronics'],
            'price_range': (50000, 500000),
            'locations': [user.state, user.district] if hasattr(user, 'state') else []
        }
    
    def content_based_recommendations(self, user_interactions, limit):
        """Content-based filtering"""
        from listings.models import Listing
        
        # Get listings matching user preferences
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
        # Simplified collaborative filtering
        from listings.models import Listing
        
        similar_users = self.find_similar_users(user)
        
        # Get items liked by similar users
        recommendations = Listing.objects.filter(
            status='active'
        ).order_by('-view_count')[:limit]
        
        return list(recommendations)
    
    def find_similar_users(self, user):
        """Find users with similar preferences"""
        # Simplified similarity calculation
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Check if user has state attribute
        if hasattr(user, 'state'):
            return User.objects.filter(
                state=user.state
            ).exclude(id=user.id)[:10]
        else:
            return User.objects.exclude(id=user.id)[:10]

# Enhanced Property models - property/models.py (continued)
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

# Jobs app extensions - jobs/models.py (additional)
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

class JobAlert(models.Model):
    """Job alerts for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_name = models.CharField(max_length=100)
    keywords = models.CharField(max_length=500)
    categories = models.ManyToManyField('JobCategory')
    location = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    experience_level = models.CharField(max_length=20, choices=[], blank=True)  # Choices would be defined in JobListing
    job_type = models.CharField(max_length=20, choices=[], blank=True)  # Choices would be defined in JobListing
    
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

# Placeholder models that are referenced but not defined
class PropertyListing(models.Model):
    """Placeholder for PropertyListing model"""
    pass

class JobCategory(models.Model):
    """Placeholder for JobCategory model"""
    pass