# Trade India Main Views
from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Count, Q
from listings.models import Listing, Category
from motors.models import MotorListing
from property.models import PropertyListing
from ai_verification.utils import get_ai_recommendations

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured listings from all categories
        try:
            context['featured_motors'] = MotorListing.objects.filter(
                is_featured=True, status='active'
            )[:8]
        except:
            context['featured_motors'] = []
        
        try:
            context['featured_properties'] = PropertyListing.objects.filter(
                is_featured=True, status='active'
            )[:6]
        except:
            context['featured_properties'] = []
        
        try:
            context['recent_listings'] = Listing.objects.filter(
                status='active'
            ).order_by('-created_at')[:12]
        except:
            context['recent_listings'] = []
        
        # AI-powered recommendations
        if self.request.user.is_authenticated:
            try:
                context['recommended_listings'] = get_ai_recommendations(
                    self.request.user
                )[:10]
            except:
                context['recommended_listings'] = []
        
        # Category statistics
        try:
            context['category_stats'] = Category.objects.annotate(
                listing_count=Count('listing')
            ).order_by('-listing_count')[:10]
        except:
            context['category_stats'] = []
        
        return context