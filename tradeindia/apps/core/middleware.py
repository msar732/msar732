"""
Custom middleware for TradeIndia
"""
from django.utils import timezone
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import pytz


class TimezoneMiddleware(MiddlewareMixin):
    """
    Activate user's timezone
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                # Get user's timezone from profile or use default
                user_timezone = getattr(request.user, 'timezone', settings.TIME_ZONE)
                timezone.activate(pytz.timezone(user_timezone))
            except:
                timezone.activate(pytz.timezone(settings.TIME_ZONE))
        else:
            # Try to get timezone from session or use default
            tzname = request.session.get('django_timezone', settings.TIME_ZONE)
            timezone.activate(pytz.timezone(tzname))


class UserActivityMiddleware(MiddlewareMixin):
    """
    Track user activity and update last activity timestamp
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # Update last activity every 5 minutes
            last_activity = request.session.get('last_activity')
            now = timezone.now()
            
            if not last_activity or (now - timezone.datetime.fromisoformat(last_activity)).seconds > 300:
                request.user.update_last_activity()
                request.session['last_activity'] = now.isoformat()


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to responses
    """
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self' https:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com "
            "https://stackpath.bootstrapcdn.com https://www.google-analytics.com https://www.googletagmanager.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://stackpath.bootstrapcdn.com "
            "https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https://api.razorpay.com https://www.google-analytics.com; "
            "frame-src 'self' https://api.razorpay.com https://www.youtube.com;"
        )
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(self), microphone=(), camera=()'
        
        # HSTS header (only in production)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Show maintenance page when site is in maintenance mode
    """
    def process_request(self, request):
        # Skip for admin and API URLs
        if request.path.startswith('/admin/') or request.path.startswith('/api/'):
            return None
        
        # Check if maintenance mode is enabled
        from apps.core.models import SiteConfiguration
        try:
            config = SiteConfiguration.get_solo()
            if config.maintenance_mode and not request.user.is_staff:
                return HttpResponse(
                    f'<html><body><h1>Site Under Maintenance</h1><p>{config.maintenance_message}</p></body></html>',
                    status=503
                )
        except:
            pass
        
        return None