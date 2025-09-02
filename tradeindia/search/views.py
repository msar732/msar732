from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q
from listings.models import Listing, Category

class SearchView(TemplateView):
    template_name = 'search/results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query:
            context['results'] = Listing.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query),
                status='active'
            ).order_by('-created_at')
            context['query'] = query
        else:
            context['results'] = Listing.objects.none()
            
        return context

class SearchSuggestionsView(TemplateView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        suggestions = []
        
        if query and len(query) >= 2:
            # Get category suggestions
            categories = Category.objects.filter(
                name__icontains=query,
                is_active=True
            )[:5]
            
            # Get listing suggestions
            listings = Listing.objects.filter(
                title__icontains=query,
                status='active'
            )[:5]
            
            suggestions = {
                'categories': [{'name': cat.name, 'slug': cat.slug} for cat in categories],
                'listings': [{'title': listing.title, 'pk': str(listing.pk), 'price': str(listing.price)} for listing in listings]
            }
        
        return JsonResponse({'suggestions': suggestions})