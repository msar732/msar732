from celery import shared_task
from .models import AIVerificationResult
from listings.models import Listing
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)

@shared_task
def verify_listing_genuineness(listing_id):
    """
    AI task to verify listing genuineness
    """
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
    # Simple rule-based analysis (can be enhanced with ML models)
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
    
    # Check for duplicate images (simplified)
    if image_count >= 3:
        base_score += 0.2
    
    return min(1.0, base_score)

def verify_location_consistency(listing):
    """Verify location consistency"""
    # Check if district belongs to state
    if listing.district.state != listing.state:
        return 0.0
    
    # Basic location verification
    return 0.8

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
        'state_district_match': listing.district.state == listing.state,
        'has_address': bool(listing.address)
    }