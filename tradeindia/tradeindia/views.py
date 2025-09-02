from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Count, Q
from listings.models import Listing, Category
from motors.models import MotorListing
from property.models import PropertyListing

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured listings from all categories
        context['featured_motors'] = MotorListing.objects.filter(
            is_featured=True, status='active'
        )[:8]
        
        context['featured_properties'] = PropertyListing.objects.filter(
            is_featured=True, status='active'
        )[:6]
        
        context['recent_listings'] = Listing.objects.filter(
            status='active'
        ).order_by('-created_at')[:12]
        
        # AI-powered recommendations
        if self.request.user.is_authenticated:
            try:
                from ai_verification.utils import get_ai_recommendations
                context['recommended_listings'] = get_ai_recommendations(
                    self.request.user
                )[:10]
            except ImportError:
                context['recommended_listings'] = []
        
        # Category statistics
        context['category_stats'] = Category.objects.annotate(
            listing_count=Count('listing')
        ).order_by('-listing_count')[:10]
        
        return context