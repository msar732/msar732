from celery import shared_task
import logging
from .models import Listing
from .ai_verification import verify_listing_content

logger = logging.getLogger(__name__)


@shared_task
def verify_listing_with_ai(listing_id):
    """
    Use AI to verify if a listing is genuine and appropriate
    """
    try:
        result = verify_listing_content(listing_id)
        if result:
            return f"Verification completed: {result.get('recommendation')}"
        else:
            return "Listing not found"
            
    except Exception as e:
        logger.error(f"Error in AI verification task for listing {listing_id}: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def update_listing_search_index(listing_id):
    """
    Update search index for a listing
    """
    try:
        listing = Listing.objects.get(id=listing_id)
        
        # Create search vector (simplified version)
        search_content = f"{listing.title} {listing.description} {listing.tags} {listing.category.name} {listing.get_location_string()}"
        listing.search_vector = search_content.lower()
        listing.save(update_fields=['search_vector'])
        
        return f"Search index updated for listing {listing_id}"
        
    except Listing.DoesNotExist:
        return f"Listing {listing_id} not found"
    except Exception as e:
        logger.error(f"Error updating search index for listing {listing_id}: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def cleanup_expired_listings():
    """
    Clean up expired listings
    """
    from django.utils import timezone
    
    expired_count = Listing.objects.filter(
        expires_at__lt=timezone.now(),
        status='active'
    ).update(status='expired')
    
    return f"Marked {expired_count} listings as expired"


@shared_task
def send_search_alerts():
    """
    Send email alerts for saved searches
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    saved_searches = SavedSearch.objects.filter(email_alerts=True).select_related('user')
    alerts_sent = 0
    
    for saved_search in saved_searches:
        # Find new listings matching the saved search
        listings = Listing.objects.filter(status='active', is_verified=True)
        
        if saved_search.query:
            listings = listings.filter(
                Q(title__icontains=saved_search.query) |
                Q(description__icontains=saved_search.query) |
                Q(tags__icontains=saved_search.query)
            )
        
        if saved_search.category:
            listings = listings.filter(category=saved_search.category)
        
        if saved_search.state:
            listings = listings.filter(state=saved_search.state)
        
        if saved_search.district:
            listings = listings.filter(district=saved_search.district)
        
        if saved_search.min_price:
            listings = listings.filter(price__gte=saved_search.min_price)
        
        if saved_search.max_price:
            listings = listings.filter(price__lte=saved_search.max_price)
        
        if saved_search.listing_type:
            listings = listings.filter(listing_type=saved_search.listing_type)
        
        # Get new listings from last 24 hours
        from datetime import timedelta
        from django.utils import timezone
        yesterday = timezone.now() - timedelta(days=1)
        new_listings = listings.filter(created_at__gte=yesterday)
        
        if new_listings.exists():
            # Send email
            subject = f"New items found for your saved search: {saved_search.name}"
            html_message = render_to_string('emails/search_alert.html', {
                'user': saved_search.user,
                'saved_search': saved_search,
                'listings': new_listings[:10],
            })
            
            try:
                send_mail(
                    subject,
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [saved_search.user.email],
                    html_message=html_message,
                    fail_silently=False
                )
                alerts_sent += 1
            except Exception as e:
                logger.error(f"Failed to send search alert to {saved_search.user.email}: {str(e)}")
    
    return f"Sent {alerts_sent} search alerts"