from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Listing, Category, State, District, ListingImage, Favorite
from .forms import ListingForm, ListingImageForm
from search.models import SearchQuery
import json

def listing_list(request):
    listings = Listing.objects.filter(status='active', is_verified=True).select_related(
        'user', 'category', 'state', 'district'
    ).prefetch_related('images')
    
    # Apply filters
    category = request.GET.get('category')
    if category:
        listings = listings.filter(category__slug=category)
    
    state = request.GET.get('state')
    if state:
        listings = listings.filter(state__code=state)
    
    district = request.GET.get('district')
    if district:
        listings = listings.filter(district__id=district)
    
    price_min = request.GET.get('price_min')
    if price_min:
        listings = listings.filter(price__gte=price_min)
    
    price_max = request.GET.get('price_max')
    if price_max:
        listings = listings.filter(price__lte=price_max)
    
    # Search
    q = request.GET.get('q')
    if q:
        listings = listings.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )
        
        # Log search query
        SearchQuery.objects.create(
            query=q,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            results_count=listings.count()
        )
    
    # Order by AI genuineness score and creation date
    listings = listings.order_by('-ai_genuineness_score', '-created_at')
    
    paginator = Paginator(listings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'listings': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'states': State.objects.all(),
    }
    
    return render(request, 'listings/list.html', context)

def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related('user', 'category', 'state', 'district')
        .prefetch_related('images'), 
        pk=pk
    )
    
    # Increment view count
    listing.view_count += 1
    listing.save(update_fields=['view_count'])
    
    # Related listings
    related_listings = Listing.objects.filter(
        category=listing.category,
        state=listing.state,
        status='active'
    ).exclude(pk=listing.pk)[:4]
    
    context = {
        'listing': listing,
        'related_listings': related_listings,
        'is_favorited': request.user.is_authenticated and 
                       Favorite.objects.filter(user=request.user, listing=listing).exists()
    }
    
    return render(request, 'listings/detail.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                ListingImage.objects.create(
                    listing=listing,
                    image=image,
                    order=i,
                    is_primary=(i == 0)
                )
            
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm()
    
    context = {
        'form': form,
        'states': State.objects.all(),
        'categories': Category.objects.filter(is_active=True)
    }
    
    return render(request, 'listings/create.html', context)

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, 
        listing=listing
    )
    
    if not created:
        favorite.delete()
        is_favorited = False
    else:
        is_favorited = True
    
    return JsonResponse({'is_favorited': is_favorited})

@require_http_methods(["GET"])
def get_districts(request):
    state_id = request.GET.get('state_id')
    districts = District.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse({'districts': list(districts)})