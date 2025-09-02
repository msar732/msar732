"""
Search views for TradeIndia
"""
from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from django.db.models import Q, Count, Avg, F, Value, CharField
from django.db.models.functions import Concat
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apps.listings.models import Listing
from apps.listings.forms import ListingSearchForm
from apps.core.models import Category, State, District, City
from .models import SearchQuery, PopularSearch, SavedSearch, SearchSuggestion
import json


class ListingSearchView(ListView):
    """Advanced search view for listings"""
    model = Listing
    template_name = 'search/results.html'
    context_object_name = 'listings'
    paginate_by = 20
    
    def get_queryset(self):
        form = ListingSearchForm(self.request.GET)
        queryset = Listing.objects.filter(status='active').select_related(
            'user', 'category', 'state', 'district', 'city'
        ).prefetch_related('images', 'tags')
        
        if form.is_valid():
            # Search query
            query = form.cleaned_data.get('q')
            if query:
                # Log search query
                self._log_search_query(query)
                
                # Full-text search on title and description
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(short_description__icontains=query) |
                    Q(tags__name__icontains=query) |
                    Q(category__name__icontains=query) |
                    Q(user__username__icontains=query) |
                    Q(user__business_name__icontains=query)
                ).distinct()
            
            # Category filter
            category = form.cleaned_data.get('category')
            if category:
                categories = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=categories)
            
            # Location filters
            state = form.cleaned_data.get('state')
            if state:
                queryset = queryset.filter(state__code=state)
            
            # Price range
            price_min = form.cleaned_data.get('price_min')
            if price_min:
                queryset = queryset.filter(price__gte=price_min)
            
            price_max = form.cleaned_data.get('price_max')
            if price_max:
                queryset = queryset.filter(price__lte=price_max)
            
            # Listing type
            listing_type = form.cleaned_data.get('listing_type')
            if listing_type:
                queryset = queryset.filter(listing_type=listing_type)
            
            # Condition
            condition = form.cleaned_data.get('condition')
            if condition:
                queryset = queryset.filter(condition=condition)
            
            # Featured only
            if form.cleaned_data.get('featured_only'):
                queryset = queryset.filter(is_featured=True)
            
            # Sorting
            sort = form.cleaned_data.get('sort', '-created_at')
            if sort == 'price_low':
                queryset = queryset.order_by('price')
            elif sort == 'price_high':
                queryset = queryset.order_by('-price')
            elif sort == 'popular':
                queryset = queryset.order_by('-views')
            elif sort == 'created_at':
                queryset = queryset.order_by('created_at')
            else:
                queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ListingSearchForm(self.request.GET)
        
        # Search query for display
        context['search_query'] = self.request.GET.get('q', '')
        
        # Suggestions
        if context['search_query']:
            context['suggestions'] = self._get_search_suggestions(context['search_query'])
        
        # Faceted search counts
        base_queryset = self.get_queryset()
        context['category_counts'] = self._get_category_counts(base_queryset)
        context['location_counts'] = self._get_location_counts(base_queryset)
        context['price_ranges'] = self._get_price_ranges(base_queryset)
        
        # Popular searches
        context['popular_searches'] = PopularSearch.objects.filter(
            is_active=True
        ).order_by('-search_count')[:10]
        
        return context
    
    def _log_search_query(self, query):
        """Log search query for analytics"""
        SearchQuery.objects.create(
            query=query,
            user=self.request.user if self.request.user.is_authenticated else None,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            results_count=0,  # Will be updated after search
            filters_applied=dict(self.request.GET),
            session_id=self.request.session.session_key or ''
        )
        
        # Update popular search counter
        popular, created = PopularSearch.objects.get_or_create(
            term=query.lower()
        )
        popular.search_count = F('search_count') + 1
        popular.save(update_fields=['search_count'])
    
    def _get_search_suggestions(self, query):
        """Get search suggestions based on query"""
        suggestions = []
        
        # Spelling corrections and synonyms
        db_suggestions = SearchSuggestion.objects.filter(
            original_query__iexact=query,
            is_active=True
        ).order_by('-confidence_score')[:5]
        
        for suggestion in db_suggestions:
            suggestions.append({
                'query': suggestion.suggested_query,
                'type': suggestion.suggestion_type
            })
        
        # Related popular searches
        related = PopularSearch.objects.filter(
            term__icontains=query.split()[0] if query else '',
            is_active=True
        ).exclude(term__iexact=query).order_by('-search_count')[:3]
        
        for term in related:
            suggestions.append({
                'query': term.term,
                'type': 'related'
            })
        
        return suggestions
    
    def _get_category_counts(self, queryset):
        """Get listing counts by category"""
        return queryset.values(
            'category__name',
            'category__slug'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
    
    def _get_location_counts(self, queryset):
        """Get listing counts by location"""
        return queryset.values(
            'state__name',
            'state__code'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
    
    def _get_price_ranges(self, queryset):
        """Get listing counts by price range"""
        ranges = [
            (0, 1000, 'Under ₹1,000'),
            (1000, 5000, '₹1,000 - ₹5,000'),
            (5000, 10000, '₹5,000 - ₹10,000'),
            (10000, 50000, '₹10,000 - ₹50,000'),
            (50000, 100000, '₹50,000 - ₹1 Lakh'),
            (100000, float('inf'), 'Above ₹1 Lakh'),
        ]
        
        counts = []
        for min_price, max_price, label in ranges:
            if max_price == float('inf'):
                count = queryset.filter(price__gte=min_price).count()
            else:
                count = queryset.filter(price__gte=min_price, price__lt=max_price).count()
            
            if count > 0:
                counts.append({
                    'label': label,
                    'count': count,
                    'min': min_price,
                    'max': max_price if max_price != float('inf') else None
                })
        
        return counts


class AutocompleteView(View):
    """Autocomplete suggestions for search"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        suggestions = []
        
        # Popular searches
        popular = PopularSearch.objects.filter(
            term__istartswith=query,
            is_active=True
        ).order_by('-search_count')[:5]
        
        for search in popular:
            suggestions.append({
                'value': search.term,
                'type': 'popular',
                'count': search.search_count
            })
        
        # Category suggestions
        categories = Category.objects.filter(
            Q(name__icontains=query) | Q(slug__icontains=query),
            is_active=True
        )[:5]
        
        for category in categories:
            suggestions.append({
                'value': category.name,
                'type': 'category',
                'url': f'/listings/category/{category.slug}/'
            })
        
        # Location suggestions
        locations = []
        
        # States
        states = State.objects.filter(
            name__icontains=query,
            is_active=True
        )[:3]
        for state in states:
            locations.append({
                'value': state.name,
                'type': 'state',
                'code': state.code
            })
        
        # Cities
        cities = City.objects.filter(
            name__icontains=query,
            is_active=True
        ).select_related('district', 'district__state')[:3]
        for city in cities:
            locations.append({
                'value': f'{city.name}, {city.district.state.name}',
                'type': 'city',
                'city': city.slug,
                'state': city.district.state.code
            })
        
        suggestions.extend(locations)
        
        # Recent listing titles
        recent = Listing.objects.filter(
            title__icontains=query,
            status='active'
        ).values('title').distinct()[:3]
        
        for listing in recent:
            suggestions.append({
                'value': listing['title'],
                'type': 'listing'
            })
        
        return JsonResponse({'suggestions': suggestions[:10]})


class SavedSearchListView(ListView):
    """List user's saved searches"""
    model = SavedSearch
    template_name = 'search/saved_searches.html'
    context_object_name = 'saved_searches'
    paginate_by = 20
    
    def get_queryset(self):
        return SavedSearch.objects.filter(
            user=self.request.user
        ).select_related('category', 'state', 'district', 'city')


@login_required
@require_POST
def save_search(request):
    """Save current search"""
    data = json.loads(request.body)
    
    saved_search = SavedSearch.objects.create(
        user=request.user,
        name=data.get('name'),
        query=data.get('query', ''),
        category_id=data.get('category'),
        state_id=data.get('state'),
        district_id=data.get('district'),
        city_id=data.get('city'),
        price_min=data.get('price_min'),
        price_max=data.get('price_max'),
        filters=data.get('filters', {}),
        alert_enabled=data.get('alert_enabled', True),
        alert_frequency=data.get('alert_frequency', 'daily')
    )
    
    return JsonResponse({
        'status': 'success',
        'search_id': saved_search.id
    })


@login_required
@require_POST
def delete_saved_search(request, pk):
    """Delete saved search"""
    saved_search = SavedSearch.objects.get(pk=pk, user=request.user)
    saved_search.delete()
    
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def toggle_search_alert(request, pk):
    """Toggle alert for saved search"""
    saved_search = SavedSearch.objects.get(pk=pk, user=request.user)
    saved_search.alert_enabled = not saved_search.alert_enabled
    saved_search.save(update_fields=['alert_enabled'])
    
    return JsonResponse({
        'status': 'success',
        'alert_enabled': saved_search.alert_enabled
    })


class SearchAnalyticsView(View):
    """Search analytics dashboard (admin only)"""
    
    def get(self, request):
        if not request.user.is_staff:
            return redirect('core:home')
        
        # Top searches
        top_searches = PopularSearch.objects.filter(
            is_active=True
        ).order_by('-search_count')[:20]
        
        # Recent searches
        recent_searches = SearchQuery.objects.select_related('user').order_by('-created_at')[:50]
        
        # Search trends (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        daily_searches = SearchQuery.objects.filter(
            created_at__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # No results searches
        no_results = SearchQuery.objects.filter(
            results_count=0,
            created_at__gte=thirty_days_ago
        ).values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:20]
        
        context = {
            'top_searches': top_searches,
            'recent_searches': recent_searches,
            'daily_searches': list(daily_searches),
            'no_results_searches': no_results,
        }
        
        return render(request, 'search/analytics.html', context)