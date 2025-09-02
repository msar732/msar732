from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.db import models
from listings.models import Listing, Category
from locations.models import State
from accounts.models import User


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured listings
        featured_listings = Listing.objects.filter(
            status='active',
            is_verified=True,
            is_featured=True
        ).select_related(
            'seller', 'category', 'state', 'district'
        ).prefetch_related('images')[:8]
        
        # Get recent listings
        recent_listings = Listing.objects.filter(
            status='active',
            is_verified=True
        ).select_related(
            'seller', 'category', 'state', 'district'
        ).prefetch_related('images').order_by('-created_at')[:8]
        
        # Get popular categories
        categories = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).annotate(
            listing_count=Count('listings', filter=models.Q(listings__status='active'))
        ).order_by('-listing_count')[:12]
        
        # Get all states for search
        states = State.objects.all().order_by('name')
        
        # Statistics
        stats = {
            'total_users': User.objects.filter(is_active=True).count(),
            'total_listings': Listing.objects.filter(status='active').count(),
            'total_locations': State.objects.count(),
        }
        
        context.update({
            'featured_listings': featured_listings,
            'recent_listings': recent_listings,
            'categories': categories,
            'states': states,
            **stats,
        })
        
        return context