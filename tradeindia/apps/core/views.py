"""
Core views for TradeIndia
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from apps.listings.models import Listing, Category
from apps.core.models import State, District, City, Page, FAQ, Advertisement
from apps.search.models import PopularSearch
import json


class HomeView(TemplateView):
    """
    Homepage view with featured listings and categories
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured listings
        context['featured_listings'] = Listing.objects.filter(
            status='active',
            is_featured=True
        ).select_related(
            'user',
            'category',
            'state',
            'district'
        ).prefetch_related('images')[:12]
        
        # Recent listings
        context['recent_listings'] = Listing.objects.filter(
            status='active'
        ).select_related(
            'user',
            'category',
            'state',
            'district'
        ).prefetch_related('images')[:20]
        
        # Popular categories with counts
        context['popular_categories'] = Category.objects.filter(
            is_active=True,
            level=0
        ).annotate(
            listing_count=Count('listings', filter=Q(listings__status='active'))
        ).order_by('-listing_count')[:8]
        
        # Popular searches
        context['popular_searches'] = PopularSearch.objects.filter(
            is_active=True
        ).order_by('-search_count')[:10]
        
        # Statistics
        context['stats'] = {
            'total_listings': cache.get_or_set(
                'total_listings',
                Listing.objects.filter(status='active').count(),
                3600
            ),
            'total_users': cache.get_or_set(
                'total_users',
                User.objects.filter(is_active=True).count(),
                3600
            ),
            'total_categories': cache.get_or_set(
                'total_categories',
                Category.objects.filter(is_active=True).count(),
                3600
            ),
            'total_cities': cache.get_or_set(
                'total_cities',
                City.objects.filter(is_active=True).count(),
                3600
            ),
        }
        
        # Homepage advertisements
        context['banner_ads'] = Advertisement.objects.filter(
            position='home_banner',
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-priority')[:3]
        
        return context


class CategoryListView(ListView):
    """
    Display all categories in a structured view
    """
    model = Category
    template_name = 'core/categories.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(
            is_active=True,
            level=0
        ).prefetch_related(
            'children'
        ).annotate(
            listing_count=Count('listings', filter=Q(listings__status='active'))
        ).order_by('order', 'name')


class LocationsView(TemplateView):
    """
    Display locations hierarchy (States -> Districts -> Cities)
    """
    template_name = 'core/locations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all states with listing counts
        context['states'] = State.objects.filter(
            is_active=True
        ).annotate(
            listing_count=Count('listings', filter=Q(listings__status='active'))
        ).order_by('name')
        
        # Get selected state if any
        state_code = self.request.GET.get('state')
        if state_code:
            state = get_object_or_404(State, code=state_code)
            context['selected_state'] = state
            context['districts'] = District.objects.filter(
                state=state,
                is_active=True
            ).annotate(
                listing_count=Count('listings', filter=Q(listings__status='active'))
            ).order_by('name')
            
            # Get selected district if any
            district_slug = self.request.GET.get('district')
            if district_slug:
                district = get_object_or_404(District, slug=district_slug, state=state)
                context['selected_district'] = district
                context['cities'] = City.objects.filter(
                    district=district,
                    is_active=True
                ).annotate(
                    listing_count=Count('listings', filter=Q(listings__status='active'))
                ).order_by('name')
        
        return context


class PageDetailView(DetailView):
    """
    Display static pages like About Us, Terms, etc.
    """
    model = Page
    template_name = 'core/page.html'
    context_object_name = 'page'
    
    def get_queryset(self):
        return Page.objects.filter(is_active=True)


class FAQView(ListView):
    """
    Display frequently asked questions
    """
    model = FAQ
    template_name = 'core/faq.html'
    context_object_name = 'faqs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)
        
        # Filter by category if specified
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('order', '-helpful_votes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faq_categories'] = Category.objects.filter(
            faqs__isnull=False,
            is_active=True
        ).distinct()
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    User dashboard
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # User stats
        context['stats'] = {
            'active_listings': user.listings.filter(status='active').count(),
            'pending_listings': user.listings.filter(status='pending').count(),
            'total_views': user.listings.aggregate(
                total=Sum('views')
            )['total'] or 0,
            'total_favorites': user.listings.aggregate(
                total=Sum('favorites')
            )['total'] or 0,
            'unread_messages': user.notifications.filter(
                is_read=False,
                notification_type='new_message'
            ).count(),
        }
        
        # Recent listings
        context['recent_listings'] = user.listings.select_related(
            'category',
            'state',
            'district'
        ).prefetch_related('images')[:10]
        
        # Recent activities
        context['recent_activities'] = []  # TODO: Implement activity stream
        
        # Saved searches
        context['saved_searches'] = user.saved_searches.filter(
            alert_enabled=True
        )[:5]
        
        return context


# AJAX Views
def get_districts(request):
    """
    Get districts for a state (AJAX)
    """
    state_code = request.GET.get('state')
    if not state_code:
        return JsonResponse({'districts': []})
    
    districts = District.objects.filter(
        state__code=state_code,
        is_active=True
    ).values('id', 'name', 'slug').order_by('name')
    
    return JsonResponse({'districts': list(districts)})


def get_cities(request):
    """
    Get cities for a district (AJAX)
    """
    district_id = request.GET.get('district')
    if not district_id:
        return JsonResponse({'cities': []})
    
    cities = City.objects.filter(
        district_id=district_id,
        is_active=True
    ).values('id', 'name', 'slug').order_by('name')
    
    return JsonResponse({'cities': list(cities)})


def get_subcategories(request):
    """
    Get subcategories for a category (AJAX)
    """
    category_id = request.GET.get('category')
    if not category_id:
        return JsonResponse({'subcategories': []})
    
    subcategories = Category.objects.filter(
        parent_id=category_id,
        is_active=True
    ).values('id', 'name', 'slug').order_by('order', 'name')
    
    return JsonResponse({'subcategories': list(subcategories)})


# Error handlers
def error_404(request, exception):
    """404 error handler"""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """500 error handler"""
    return render(request, 'errors/500.html', status=500)


def error_403(request, exception):
    """403 error handler"""
    return render(request, 'errors/403.html', status=403)


def error_400(request, exception):
    """400 error handler"""
    return render(request, 'errors/400.html', status=400)


# Sitemap views
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.5
    changefreq = 'daily'
    
    def items(self):
        return ['core:home', 'core:categories', 'core:locations', 'core:faq']
    
    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Category.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.modified_at


class ListingSitemap(Sitemap):
    """Sitemap for listings"""
    changefreq = 'daily'
    priority = 0.9
    
    def items(self):
        return Listing.objects.filter(status='active')
    
    def lastmod(self, obj):
        return obj.modified_at