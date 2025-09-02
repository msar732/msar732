# AI-powered recommendation system - ai_verification/ml_models.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache
from django.db import models
import joblib
import os

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
            'locations': [user.state, user.district]
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
        
        return User.objects.filter(
            state=user.state
        ).exclude(id=user.id)[:10]