from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from listings.models import Listing, Category, State, District
from django.core.paginator import Paginator

def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get suggestions from different sources
    categories = Category.objects.filter(
        name__icontains=query, is_active=True
    )[:5].values('name', 'slug')
    
    listings = Listing.objects.filter(
        Q(title__icontains=query) & Q(status='active')
    )[:10].values('title', 'pk')
    
    locations = State.objects.filter(name__icontains=query)[:5].values('name', 'code')
    
    suggestions = {
        'categories': list(categories),
        'listings': list(listings),
        'locations': list(locations)
    }
    
    return JsonResponse({'suggestions': suggestions})

def advanced_search(request):
    context = {
        'categories': Category.objects.filter(is_active=True),
        'states': State.objects.all(),
    }
    return render(request, 'search/advanced.html', context)