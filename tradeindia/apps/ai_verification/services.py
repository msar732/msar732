"""
AI Verification services for listing authenticity
"""
import numpy as np
import cv2
import tensorflow as tf
from PIL import Image
import pytesseract
import hashlib
import requests
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from .models import (
    AIVerificationLog, FraudPattern, ImageAnalysis, 
    TextAnalysis, PriceAnalysis, UserTrustScore
)
from apps.listings.models import Listing, ListingImage
import re
import json
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AIVerificationService:
    """Main AI verification service"""
    
    def __init__(self):
        self.image_model = None
        self.text_model = None
        self.load_models()
    
    def load_models(self):
        """Load AI models"""
        try:
            # Load pre-trained models
            # In production, these would be custom trained models
            pass
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
    
    def verify_listing(self, listing: Listing) -> Dict:
        """
        Perform comprehensive AI verification of a listing
        """
        verification_log = AIVerificationLog.objects.create(
            listing=listing,
            verification_type='listing',
            status='processing'
        )
        
        try:
            start_time = timezone.now()
            
            # Run all verification checks
            image_results = self._verify_images(listing)
            text_results = self._verify_text(listing)
            price_results = self._verify_price(listing)
            user_results = self._verify_user(listing.user)
            fraud_results = self._check_fraud_patterns(listing)
            
            # Calculate overall confidence score
            confidence_scores = [
                image_results.get('confidence', 0.5),
                text_results.get('confidence', 0.5),
                price_results.get('confidence', 0.5),
                user_results.get('trust_score', 50) / 100,
            ]
            
            overall_confidence = np.mean(confidence_scores)
            
            # Determine if listing is genuine
            is_genuine = (
                overall_confidence > settings.AI_CONFIDENCE_THRESHOLD and
                not fraud_results.get('high_risk_patterns', []) and
                image_results.get('all_images_genuine', True) and
                text_results.get('is_genuine', True)
            )
            
            # Calculate risk score
            risk_factors = []
            if image_results.get('stock_photos_detected'):
                risk_factors.append('Stock photos detected')
            if image_results.get('duplicates_found'):
                risk_factors.append('Duplicate images found')
            if text_results.get('spam_detected'):
                risk_factors.append('Spam content detected')
            if price_results.get('suspicious_pricing'):
                risk_factors.append('Suspicious pricing')
            if fraud_results.get('patterns_matched'):
                risk_factors.extend(fraud_results.get('patterns_matched', []))
            
            risk_score = min(len(risk_factors) * 0.2, 1.0)
            
            # Update verification log
            verification_log.status = 'completed'
            verification_log.is_genuine = is_genuine
            verification_log.confidence_score = overall_confidence
            verification_log.risk_score = risk_score
            verification_log.analysis_results = {
                'image_analysis': image_results,
                'text_analysis': text_results,
                'price_analysis': price_results,
                'user_analysis': user_results,
                'fraud_analysis': fraud_results,
            }
            verification_log.detected_issues = risk_factors
            verification_log.recommendations = self._generate_recommendations(
                listing, risk_factors
            )
            verification_log.processing_time = (
                timezone.now() - start_time
            ).total_seconds()
            verification_log.save()
            
            # Update listing
            listing.ai_verified = True
            listing.ai_confidence_score = overall_confidence
            listing.ai_verification_date = timezone.now()
            listing.save(update_fields=[
                'ai_verified', 
                'ai_confidence_score', 
                'ai_verification_date'
            ])
            
            return {
                'success': True,
                'is_genuine': is_genuine,
                'confidence_score': overall_confidence,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'verification_id': verification_log.id
            }
            
        except Exception as e:
            logger.error(f"Error verifying listing {listing.id}: {e}")
            verification_log.status = 'failed'
            verification_log.error_message = str(e)
            verification_log.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _verify_images(self, listing: Listing) -> Dict:
        """Verify listing images using AI"""
        results = {
            'all_images_genuine': True,
            'confidence': 1.0,
            'stock_photos_detected': False,
            'duplicates_found': False,
            'inappropriate_content': False,
            'image_analyses': []
        }
        
        images = listing.images.all()
        if not images:
            results['confidence'] = 0.5
            return results
        
        confidence_scores = []
        
        for image_obj in images:
            analysis = self._analyze_single_image(image_obj)
            results['image_analyses'].append(analysis)
            
            # Update flags
            if analysis.get('is_stock_photo'):
                results['stock_photos_detected'] = True
                results['all_images_genuine'] = False
            
            if analysis.get('is_duplicate'):
                results['duplicates_found'] = True
                results['all_images_genuine'] = False
            
            if analysis.get('is_inappropriate'):
                results['inappropriate_content'] = True
                results['all_images_genuine'] = False
            
            confidence_scores.append(analysis.get('confidence', 0.5))
        
        results['confidence'] = np.mean(confidence_scores)
        return results
    
    def _analyze_single_image(self, image_obj: ListingImage) -> Dict:
        """Analyze a single image"""
        try:
            # Open image
            img = Image.open(image_obj.image.path)
            img_array = np.array(img)
            
            # Basic quality checks
            quality_score = self._assess_image_quality(img_array)
            
            # Check for stock photo indicators
            is_stock = self._detect_stock_photo(img_array)
            
            # Check for watermarks
            has_watermark = self._detect_watermark(img_array)
            
            # Extract text from image
            extracted_text = self._extract_text_from_image(img_array)
            
            # Check for duplicates
            is_duplicate, duplicate_of = self._check_image_duplicate(image_obj)
            
            # Detect objects in image
            detected_objects = self._detect_objects(img_array)
            
            # Content moderation
            is_inappropriate, moderation_labels = self._moderate_image_content(img_array)
            
            # Calculate confidence
            confidence = quality_score
            if is_stock or has_watermark:
                confidence *= 0.5
            if is_duplicate:
                confidence *= 0.3
            
            # Save analysis
            analysis, created = ImageAnalysis.objects.update_or_create(
                image=image_obj,
                defaults={
                    'detected_objects': detected_objects,
                    'detected_text': extracted_text,
                    'quality_score': quality_score,
                    'is_stock_photo': is_stock,
                    'is_watermarked': has_watermark,
                    'is_duplicate': is_duplicate,
                    'duplicate_of': duplicate_of,
                    'is_inappropriate': is_inappropriate,
                    'moderation_labels': moderation_labels,
                    'processing_time': 0.1  # Placeholder
                }
            )
            
            return {
                'image_id': image_obj.id,
                'confidence': confidence,
                'quality_score': quality_score,
                'is_stock_photo': is_stock,
                'has_watermark': has_watermark,
                'is_duplicate': is_duplicate,
                'is_inappropriate': is_inappropriate,
                'detected_objects': detected_objects,
                'extracted_text': extracted_text
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_obj.id}: {e}")
            return {
                'image_id': image_obj.id,
                'confidence': 0.5,
                'error': str(e)
            }
    
    def _assess_image_quality(self, img_array: np.ndarray) -> float:
        """Assess image quality metrics"""
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Calculate blur score using Laplacian
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = min(laplacian_var / 1000, 1.0)
        
        # Calculate brightness
        brightness = np.mean(gray) / 255
        brightness_score = 1.0 - abs(brightness - 0.5) * 2
        
        # Calculate contrast
        contrast = gray.std() / 255
        contrast_score = min(contrast * 4, 1.0)
        
        # Combined quality score
        quality_score = (blur_score + brightness_score + contrast_score) / 3
        
        return quality_score
    
    def _detect_stock_photo(self, img_array: np.ndarray) -> bool:
        """Detect if image is likely a stock photo"""
        # Look for common stock photo indicators:
        # - Perfect lighting and composition
        # - Watermarks or logos
        # - Generic subjects
        # This is a simplified implementation
        
        # Check for too-perfect histogram distribution
        hist = cv2.calcHist([img_array], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = hist.flatten()
        hist = hist / hist.sum()
        
        # Stock photos often have very uniform histograms
        uniformity = 1.0 - hist.std()
        
        return uniformity > 0.85
    
    def _detect_watermark(self, img_array: np.ndarray) -> bool:
        """Detect watermarks in image"""
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for text patterns in edges
        # This is a simplified implementation
        edge_density = np.sum(edges > 0) / edges.size
        
        # Watermarks often create consistent edge patterns
        return edge_density > 0.3
    
    def _extract_text_from_image(self, img_array: np.ndarray) -> str:
        """Extract text from image using OCR"""
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(img_array)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(pil_image)
            
            # Clean extracted text
            text = ' '.join(text.split())
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def _check_image_duplicate(self, image_obj: ListingImage) -> Tuple[bool, Optional[ListingImage]]:
        """Check if image is duplicate of existing image"""
        # Calculate image hash
        img = Image.open(image_obj.image.path)
        img_hash = self._calculate_image_hash(img)
        
        # Look for similar images
        # In production, this would use a more sophisticated similarity search
        similar_images = ListingImage.objects.exclude(
            id=image_obj.id
        ).filter(
            listing__status='active'
        )[:100]  # Limit search for performance
        
        for other_image in similar_images:
            try:
                other_img = Image.open(other_image.image.path)
                other_hash = self._calculate_image_hash(other_img)
                
                # Calculate similarity
                similarity = self._calculate_hash_similarity(img_hash, other_hash)
                
                if similarity > 0.95:  # 95% similar
                    return True, other_image
            except:
                continue
        
        return False, None
    
    def _calculate_image_hash(self, img: Image) -> str:
        """Calculate perceptual hash of image"""
        # Resize to 8x8
        img = img.resize((8, 8), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Get pixel values
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        
        # Create hash
        bits = ''.join(['1' if pixel > avg else '0' for pixel in pixels])
        
        return bits
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two image hashes"""
        if len(hash1) != len(hash2):
            return 0.0
        
        matching_bits = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matching_bits / len(hash1)
    
    def _detect_objects(self, img_array: np.ndarray) -> List[Dict]:
        """Detect objects in image"""
        # In production, this would use a trained object detection model
        # For now, return placeholder data
        return [
            {'object': 'general_item', 'confidence': 0.8}
        ]
    
    def _moderate_image_content(self, img_array: np.ndarray) -> Tuple[bool, List[str]]:
        """Check for inappropriate content"""
        # In production, this would use a content moderation API or model
        # For now, return safe defaults
        return False, []
    
    def _verify_text(self, listing: Listing) -> Dict:
        """Verify listing text content"""
        results = {
            'is_genuine': True,
            'confidence': 1.0,
            'spam_detected': False,
            'issues': []
        }
        
        # Combine all text
        text = f"{listing.title} {listing.description} {listing.short_description or ''}"
        
        # Check for spam patterns
        spam_score = self._calculate_spam_score(text)
        if spam_score > 0.7:
            results['spam_detected'] = True
            results['is_genuine'] = False
            results['issues'].append('Spam content detected')
        
        # Check for suspicious patterns
        suspicious_patterns = self._check_suspicious_text_patterns(text)
        if suspicious_patterns:
            results['is_genuine'] = False
            results['issues'].extend(suspicious_patterns)
        
        # Extract contact information
        contacts = self._extract_contact_info(text)
        
        # Language analysis
        language_quality = self._analyze_language_quality(text)
        
        # Category relevance
        category_relevance = self._check_category_relevance(text, listing.category)
        
        # Calculate confidence
        results['confidence'] = (
            (1.0 - spam_score) * 0.4 +
            language_quality * 0.3 +
            category_relevance * 0.3
        )
        
        # Save analysis
        TextAnalysis.objects.update_or_create(
            listing=listing,
            defaults={
                'sentiment_score': 0.0,  # Placeholder
                'spam_score': spam_score,
                'is_spam': spam_score > 0.7,
                'suspicious_phrases': suspicious_patterns,
                'contains_phone': bool(contacts.get('phones')),
                'contains_email': bool(contacts.get('emails')),
                'contains_url': bool(contacts.get('urls')),
                'extracted_contacts': contacts,
                'category_relevance_score': category_relevance,
            }
        )
        
        return results
    
    def _calculate_spam_score(self, text: str) -> float:
        """Calculate spam score for text"""
        spam_indicators = [
            r'earn money fast',
            r'work from home',
            r'guaranteed income',
            r'click here now',
            r'limited time offer',
            r'act now',
            r'100% free',
            r'no experience needed',
            r'make \$\d+ per day',
            r'whatsapp me',
            r'dm for price',
        ]
        
        text_lower = text.lower()
        matches = 0
        
        for pattern in spam_indicators:
            if re.search(pattern, text_lower):
                matches += 1
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            matches += 1
        
        # Check for excessive punctuation
        punct_ratio = sum(1 for c in text if c in '!?') / max(len(text), 1)
        if punct_ratio > 0.05:
            matches += 1
        
        return min(matches / 5, 1.0)
    
    def _check_suspicious_text_patterns(self, text: str) -> List[str]:
        """Check for suspicious patterns in text"""
        suspicious = []
        
        patterns = [
            (r'urgently selling', 'Urgency pattern detected'),
            (r'leaving country', 'Common scam pattern'),
            (r'first come first serve', 'Pressure tactic detected'),
            (r'no bargaining', 'Inflexibility indicator'),
            (r'only serious buyers', 'Exclusivity pattern'),
        ]
        
        text_lower = text.lower()
        for pattern, message in patterns:
            if re.search(pattern, text_lower):
                suspicious.append(message)
        
        return suspicious
    
    def _extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """Extract contact information from text"""
        contacts = {
            'phones': [],
            'emails': [],
            'urls': []
        }
        
        # Phone patterns
        phone_patterns = [
            r'\+91[\s-]?\d{10}',
            r'\d{10}',
            r'\d{5}[\s-]\d{5}',
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            contacts['phones'].extend(phones)
        
        # Email pattern
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        contacts['emails'] = emails
        
        # URL pattern
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        contacts['urls'] = urls
        
        return contacts
    
    def _analyze_language_quality(self, text: str) -> float:
        """Analyze language quality"""
        # Simple quality metrics
        words = text.split()
        
        if len(words) < 10:
            return 0.3
        
        # Check for repetition
        unique_words = set(words)
        uniqueness_ratio = len(unique_words) / len(words)
        
        # Check for very short or very long description
        if len(words) < 20:
            length_score = 0.5
        elif len(words) > 500:
            length_score = 0.7
        else:
            length_score = 1.0
        
        return (uniqueness_ratio + length_score) / 2
    
    def _check_category_relevance(self, text: str, category) -> float:
        """Check if text is relevant to category"""
        # In production, this would use NLP models
        # For now, simple keyword matching
        
        category_keywords = {
            'electronics': ['phone', 'laptop', 'computer', 'tablet', 'camera', 'tv'],
            'vehicles': ['car', 'bike', 'motorcycle', 'scooter', 'vehicle'],
            'real estate': ['house', 'flat', 'apartment', 'land', 'property', 'rent'],
            'fashion': ['dress', 'shirt', 'shoes', 'clothing', 'wear'],
        }
        
        text_lower = text.lower()
        category_name = category.name.lower()
        
        if category_name in category_keywords:
            keywords = category_keywords[category_name]
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            return min(matches / 3, 1.0)
        
        return 0.5
    
    def _verify_price(self, listing: Listing) -> Dict:
        """Verify listing price"""
        results = {
            'confidence': 1.0,
            'suspicious_pricing': False,
            'issues': []
        }
        
        # Get similar listings
        similar_listings = Listing.objects.filter(
            category=listing.category,
            status='active',
            state=listing.state
        ).exclude(id=listing.id)
        
        if similar_listings.count() < 5:
            # Not enough data for comparison
            results['confidence'] = 0.5
            return results
        
        # Calculate market statistics
        prices = list(similar_listings.values_list('price', flat=True))
        market_avg = np.mean(prices)
        market_std = np.std(prices)
        market_min = np.min(prices)
        market_max = np.max(prices)
        
        # Check if price is within reasonable range
        z_score = abs((float(listing.price) - market_avg) / max(market_std, 1))
        
        if z_score > 3:  # More than 3 standard deviations
            results['suspicious_pricing'] = True
            results['issues'].append('Price significantly differs from market average')
            results['confidence'] = 0.3
        elif z_score > 2:
            results['confidence'] = 0.7
        
        # Check for round number pricing
        if listing.price % 1000 == 0 and listing.price > 10000:
            results['issues'].append('Suspiciously round pricing')
            results['confidence'] *= 0.9
        
        # Save analysis
        PriceAnalysis.objects.update_or_create(
            listing=listing,
            defaults={
                'market_average': market_avg,
                'market_min': market_min,
                'market_max': market_max,
                'is_overpriced': float(listing.price) > market_avg + 2 * market_std,
                'is_underpriced': float(listing.price) < market_avg - 2 * market_std,
                'price_score': 1.0 - min(z_score / 3, 1.0),
                'confidence_level': results['confidence'],
            }
        )
        
        return results
    
    def _verify_user(self, user) -> Dict:
        """Verify user trustworthiness"""
        # Get or create trust score
        trust_score, created = UserTrustScore.objects.get_or_create(
            user=user,
            defaults={'trust_score': 50.0}
        )
        
        # Calculate trust score components
        components = {
            'account_age': self._calculate_account_age_score(user),
            'verification_status': self._calculate_verification_score(user),
            'listing_history': self._calculate_listing_history_score(user),
            'behavior_patterns': self._calculate_behavior_score(user),
        }
        
        # Update trust score
        trust_score.trust_score = sum(components.values()) / len(components) * 100
        trust_score.score_components = components
        trust_score.save()
        
        return {
            'trust_score': trust_score.trust_score,
            'components': components
        }
    
    def _calculate_account_age_score(self, user) -> float:
        """Calculate score based on account age"""
        account_age = (timezone.now() - user.date_joined).days
        
        if account_age < 7:
            return 0.2
        elif account_age < 30:
            return 0.5
        elif account_age < 180:
            return 0.8
        else:
            return 1.0
    
    def _calculate_verification_score(self, user) -> float:
        """Calculate score based on verification status"""
        score = 0.0
        
        if user.email_verified:
            score += 0.25
        if user.phone_verified:
            score += 0.25
        if user.identity_verified:
            score += 0.25
        if user.is_business_user and user.business_verified:
            score += 0.25
        elif not user.is_business_user:
            score += 0.25
        
        return score
    
    def _calculate_listing_history_score(self, user) -> float:
        """Calculate score based on listing history"""
        total_listings = user.listings.count()
        active_listings = user.listings.filter(status='active').count()
        reported_listings = user.listings.filter(reports__status='action_taken').distinct().count()
        
        if total_listings == 0:
            return 0.5
        
        # Penalize for too many reported listings
        report_ratio = reported_listings / total_listings
        
        if report_ratio > 0.2:
            return 0.2
        elif report_ratio > 0.1:
            return 0.5
        else:
            return 0.9
    
    def _calculate_behavior_score(self, user) -> float:
        """Calculate score based on user behavior"""
        # In production, this would analyze user activity patterns
        # For now, return a default score
        return 0.7
    
    def _check_fraud_patterns(self, listing: Listing) -> Dict:
        """Check against known fraud patterns"""
        patterns_matched = []
        high_risk_patterns = []
        
        # Get active fraud patterns
        patterns = FraudPattern.objects.filter(is_active=True)
        
        for pattern in patterns:
            if self._match_fraud_pattern(listing, pattern):
                patterns_matched.append(pattern.name)
                
                if pattern.severity >= 8:
                    high_risk_patterns.append(pattern.name)
                
                # Update pattern statistics
                pattern.detection_count = models.F('detection_count') + 1
                pattern.save(update_fields=['detection_count'])
        
        return {
            'patterns_matched': patterns_matched,
            'high_risk_patterns': high_risk_patterns,
            'risk_level': 'high' if high_risk_patterns else 'medium' if patterns_matched else 'low'
        }
    
    def _match_fraud_pattern(self, listing: Listing, pattern: FraudPattern) -> bool:
        """Check if listing matches a fraud pattern"""
        pattern_data = pattern.pattern_data
        
        if pattern.pattern_type == 'title':
            return self._match_text_pattern(listing.title, pattern_data)
        elif pattern.pattern_type == 'description':
            return self._match_text_pattern(listing.description, pattern_data)
        elif pattern.pattern_type == 'price':
            return self._match_price_pattern(listing.price, pattern_data)
        # Add more pattern types as needed
        
        return False
    
    def _match_text_pattern(self, text: str, pattern_data: Dict) -> bool:
        """Match text against pattern"""
        if 'regex' in pattern_data:
            return bool(re.search(pattern_data['regex'], text, re.IGNORECASE))
        
        if 'keywords' in pattern_data:
            text_lower = text.lower()
            matches = sum(1 for keyword in pattern_data['keywords'] if keyword in text_lower)
            threshold = pattern_data.get('threshold', 1)
            return matches >= threshold
        
        return False
    
    def _match_price_pattern(self, price: float, pattern_data: Dict) -> bool:
        """Match price against pattern"""
        if 'min' in pattern_data and price < pattern_data['min']:
            return True
        
        if 'max' in pattern_data and price > pattern_data['max']:
            return True
        
        if 'suspicious_values' in pattern_data:
            return float(price) in pattern_data['suspicious_values']
        
        return False
    
    def _generate_recommendations(self, listing: Listing, risk_factors: List[str]) -> List[str]:
        """Generate recommendations based on risk factors"""
        recommendations = []
        
        if 'Stock photos detected' in risk_factors:
            recommendations.append('Upload original photos of the actual item')
        
        if 'Duplicate images found' in risk_factors:
            recommendations.append('Remove duplicate images and add unique photos')
        
        if 'Spam content detected' in risk_factors:
            recommendations.append('Rewrite description with clear, honest information')
        
        if 'Suspicious pricing' in risk_factors:
            recommendations.append('Adjust price to match market rates')
        
        if not recommendations:
            recommendations.append('Listing looks good! Consider adding more details to attract buyers')
        
        return recommendations


# Celery tasks for async processing
from celery import shared_task

@shared_task
def verify_listing_async(listing_id: int):
    """Asynchronously verify a listing"""
    try:
        listing = Listing.objects.get(id=listing_id)
        service = AIVerificationService()
        return service.verify_listing(listing)
    except Listing.DoesNotExist:
        logger.error(f"Listing {listing_id} not found")
        return {'success': False, 'error': 'Listing not found'}


@shared_task
def batch_verify_listings():
    """Batch verify unverified listings"""
    unverified_listings = Listing.objects.filter(
        status='active',
        ai_verified=False
    ).order_by('-created_at')[:100]
    
    service = AIVerificationService()
    results = []
    
    for listing in unverified_listings:
        result = service.verify_listing(listing)
        results.append({
            'listing_id': listing.id,
            'success': result.get('success'),
            'is_genuine': result.get('is_genuine')
        })
    
    return results


@shared_task
def update_user_trust_scores():
    """Periodically update user trust scores"""
    from apps.accounts.models import User
    
    # Update trust scores for active users
    active_users = User.objects.filter(
        is_active=True,
        last_activity__gte=timezone.now() - timezone.timedelta(days=30)
    )
    
    service = AIVerificationService()
    
    for user in active_users:
        service._verify_user(user)
    
    return f"Updated trust scores for {active_users.count()} users"