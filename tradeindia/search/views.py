from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SearchLog, PopularSearch, SearchSuggestion
from listings.models import Listing, SavedSearch, Category
from locations.models import State, District
from .serializers import SearchLogSerializer, PopularSearchSerializer
from listings.serializers import ListingSerializer, SavedSearchSerializer


class SearchView(TemplateView):
    """Main search view"""
    template_name = 'search/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        category = self.request.GET.get('category')
        state = self.request.GET.get('state')
        district = self.request.GET.get('district')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        listing_type = self.request.GET.get('listing_type')
        
        listings = Listing.objects.filter(status='active', is_verified=True)
        
        # Apply search filters
        if query:
            listings = listings.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )
        
        if category:
            listings = listings.filter(category_id=category)
        
        if state:
            listings = listings.filter(state_id=state)
        
        if district:
            listings = listings.filter(district_id=district)
        
        if min_price:
            try:
                listings = listings.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                listings = listings.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        if listing_type:
            listings = listings.filter(listing_type=listing_type)
        
        # Order results
        order_by = self.request.GET.get('order_by', '-created_at')
        if order_by in ['created_at', '-created_at', 'price', '-price', 'views', '-views']:
            listings = listings.order_by(order_by)
        
        listings = listings.select_related(
            'seller', 'category', 'state', 'district', 'city'
        ).prefetch_related('images')
        
        # Log search
        if query or category or state:
            SearchLog.objects.create(
                user=self.request.user if self.request.user.is_authenticated else None,
                query=query,
                category=Category.objects.get(id=category).name if category else '',
                location=f"{State.objects.get(id=state).name if state else ''} {District.objects.get(id=district).name if district else ''}".strip(),
                results_count=listings.count(),
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Update popular search
            if query:
                popular_search, created = PopularSearch.objects.get_or_create(
                    query=query,
                    defaults={'search_count': 1}
                )
                if not created:
                    popular_search.search_count += 1
                    popular_search.save()
        
        context.update({
            'listings': listings,
            'query': query,
            'categories': Category.objects.filter(is_active=True, parent__isnull=True),
            'states': State.objects.all(),
            'listing_types': Listing.LISTING_TYPE_CHOICES,
            'results_count': listings.count(),
            'current_filters': self.request.GET,
        })
        
        return context
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class SearchSuggestionsView(APIView):
    """API view for search suggestions"""
    
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return Response([])
        
        # Get suggestions from SearchSuggestion model
        suggestions = SearchSuggestion.objects.filter(
            text__icontains=query,
            is_active=True
        ).order_by('-popularity_score')[:10]
        
        # Also get suggestions from listing titles
        listing_suggestions = Listing.objects.filter(
            title__icontains=query,
            status='active',
            is_verified=True
        ).values_list('title', flat=True).distinct()[:5]
        
        # Combine suggestions
        all_suggestions = list(suggestions.values_list('text', flat=True)) + list(listing_suggestions)
        
        return Response(all_suggestions[:10])


class PopularSearchesView(APIView):
    """API view for popular searches"""
    
    def get(self, request):
        popular_searches = PopularSearch.objects.order_by('-search_count')[:20]
        return Response([{'query': ps.query, 'count': ps.search_count} for ps in popular_searches])


class SaveSearchView(LoginRequiredMixin, APIView):
    """Save a search for notifications"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = SavedSearchSerializer(data=request.data)
        if serializer.is_valid():
            saved_search = serializer.save(user=request.user)
            return Response(SavedSearchSerializer(saved_search).data, status=201)
        return Response(serializer.errors, status=400)


class SavedSearchesView(LoginRequiredMixin, TemplateView):
    """View for user's saved searches"""
    template_name = 'search/saved_searches.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['saved_searches'] = SavedSearch.objects.filter(
            user=self.request.user
        ).select_related('category', 'state', 'district').order_by('-created_at')
        return context