"""
AI-powered listing verification system
"""

import openai
import json
import logging
from django.conf import settings
from .models import Listing

logger = logging.getLogger(__name__)


class AIVerificationService:
    """Service class for AI-powered listing verification"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OpenAI API key not configured")
    
    def verify_listing(self, listing):
        """
        Verify a listing using AI analysis
        Returns: dict with verification results
        """
        if not self.client:
            return self._fallback_verification(listing)
        
        try:
            # Prepare content for AI analysis
            content = self._prepare_listing_content(listing)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            result = self._parse_ai_response(ai_response)
            
            # Apply verification result
            self._apply_verification_result(listing, result)
            
            return result
            
        except Exception as e:
            logger.error(f"AI verification failed for listing {listing.id}: {str(e)}")
            return self._fallback_verification(listing)
    
    def _prepare_listing_content(self, listing):
        """Prepare listing content for AI analysis"""
        return f"""
        Title: {listing.title}
        Description: {listing.description}
        Category: {listing.category.name}
        Price: ₹{listing.price} {listing.currency}
        Location: {listing.get_location_string()}
        Listing Type: {listing.get_listing_type_display()}
        Tags: {listing.tags}
        Seller: {listing.seller.username} (Rating: {listing.seller.rating}/5)
        """
    
    def _get_system_prompt(self):
        """Get the system prompt for AI verification"""
        return """You are an AI content moderator for Trade India, a trading platform in India. 
        Analyze the listing content and determine if it's genuine, appropriate, and follows platform guidelines.
        
        Consider these factors:
        1. Is the description realistic and detailed enough?
        2. Is the price reasonable for the item and location in India?
        3. Does it contain any suspicious, inappropriate, or illegal content?
        4. Is it likely a scam, fake listing, or spam?
        5. Does the category match the item description?
        6. Are there any red flags in the content?
        
        Respond ONLY with a valid JSON object containing:
        {
            "is_genuine": boolean,
            "score": number (0-100),
            "issues": ["list", "of", "issues"],
            "recommendation": "approve|review|reject",
            "reasoning": "brief explanation"
        }
        
        Guidelines:
        - Score 80+ with no major issues = approve
        - Score 30-79 or minor issues = review
        - Score <30 or major issues = reject
        """
    
    def _parse_ai_response(self, ai_response):
        """Parse AI response into structured data"""
        try:
            # Try to extract JSON from response
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '')
            
            result = json.loads(ai_response.strip())
            
            # Validate required fields
            required_fields = ['is_genuine', 'score', 'recommendation']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure score is within valid range
            result['score'] = max(0, min(100, result.get('score', 0)))
            
            # Ensure recommendation is valid
            if result['recommendation'] not in ['approve', 'review', 'reject']:
                result['recommendation'] = 'review'
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return {
                'is_genuine': False,
                'score': 50,
                'issues': ['AI parsing error'],
                'recommendation': 'review',
                'reasoning': 'AI analysis failed, manual review required'
            }
    
    def _apply_verification_result(self, listing, result):
        """Apply verification result to listing"""
        listing.ai_verification_score = result.get('score', 0)
        listing.verification_notes = result.get('reasoning', '')
        
        if result.get('issues'):
            listing.verification_notes += f" Issues: {', '.join(result['issues'])}"
        
        # Set status based on recommendation
        if result.get('recommendation') == 'approve' and result.get('score', 0) >= 80:
            listing.is_verified = True
            listing.status = 'active'
        elif result.get('recommendation') == 'reject' or result.get('score', 0) < 30:
            listing.status = 'suspended'
            listing.verification_notes += " - Flagged by AI for review"
        else:
            listing.status = 'pending_verification'
        
        listing.save()
        
        logger.info(f"AI verification completed for listing {listing.id}: {result.get('recommendation')}")
    
    def _fallback_verification(self, listing):
        """Fallback verification when AI is not available"""
        # Simple rule-based verification
        score = 70  # Default score
        issues = []
        
        # Check title length
        if len(listing.title) < 10:
            issues.append("Title too short")
            score -= 10
        
        # Check description length
        if len(listing.description) < 50:
            issues.append("Description too short")
            score -= 15
        
        # Check price reasonableness (basic check)
        if listing.price <= 0:
            issues.append("Invalid price")
            score -= 30
        elif listing.price > 10000000:  # 1 crore
            issues.append("Price seems too high")
            score -= 20
        
        # Determine recommendation
        if score >= 70 and not issues:
            recommendation = 'approve'
            listing.is_verified = True
            listing.status = 'active'
        elif score >= 50:
            recommendation = 'review'
            listing.status = 'pending_verification'
        else:
            recommendation = 'reject'
            listing.status = 'suspended'
        
        result = {
            'is_genuine': score >= 50,
            'score': score,
            'issues': issues,
            'recommendation': recommendation,
            'reasoning': 'Fallback verification (AI not available)'
        }
        
        listing.ai_verification_score = score
        listing.verification_notes = result['reasoning']
        if issues:
            listing.verification_notes += f" Issues: {', '.join(issues)}"
        listing.save()
        
        return result


def verify_listing_content(listing_id):
    """
    Standalone function to verify listing content
    Can be called from Celery tasks or views
    """
    try:
        listing = Listing.objects.get(id=listing_id)
        service = AIVerificationService()
        return service.verify_listing(listing)
    except Listing.DoesNotExist:
        logger.error(f"Listing {listing_id} not found for verification")
        return None


def batch_verify_listings(listing_ids):
    """
    Verify multiple listings in batch
    Useful for processing existing listings
    """
    results = []
    service = AIVerificationService()
    
    for listing_id in listing_ids:
        try:
            listing = Listing.objects.get(id=listing_id)
            result = service.verify_listing(listing)
            results.append({
                'listing_id': listing_id,
                'result': result
            })
        except Listing.DoesNotExist:
            logger.error(f"Listing {listing_id} not found")
            continue
    
    return results


def get_verification_stats():
    """Get verification statistics"""
    from django.db.models import Count, Avg
    
    stats = Listing.objects.aggregate(
        total=Count('id'),
        verified=Count('id', filter=models.Q(is_verified=True)),
        pending=Count('id', filter=models.Q(status='pending_verification')),
        suspended=Count('id', filter=models.Q(status='suspended')),
        avg_score=Avg('ai_verification_score')
    )
    
    stats['verification_rate'] = (stats['verified'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    return stats