"""
Context processors for TradeIndia
"""
from django.conf import settings
from apps.core.models import SiteConfiguration, Category
from apps.notifications.models import UserNotification


def site_settings(request):
    """
    Add site configuration to context
    """
    try:
        config = SiteConfiguration.get_solo()
    except:
        config = None
    
    return {
        'site_config': config,
        'site_name': config.site_name if config else 'TradeIndia',
        'tagline': config.tagline if config else 'Buy and Sell Anything in India',
    }


def categories(request):
    """
    Add main categories to context for navigation
    """
    main_categories = Category.objects.filter(
        parent=None,
        is_active=True
    ).order_by('order', 'name')[:12]
    
    return {
        'main_categories': main_categories,
    }


def notifications(request):
    """
    Add unread notifications count to context
    """
    if request.user.is_authenticated:
        unread_count = UserNotification.objects.filter(
            recipient=request.user,
            is_read=False,
            is_archived=False
        ).count()
        
        recent_notifications = UserNotification.objects.filter(
            recipient=request.user,
            is_archived=False
        ).select_related('sender', 'related_listing')[:5]
    else:
        unread_count = 0
        recent_notifications = []
    
    return {
        'unread_notifications_count': unread_count,
        'recent_notifications': recent_notifications,
    }