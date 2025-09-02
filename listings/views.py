from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Listing, ListingImage, Category, State, District
from .forms import ListingForm


 


def listing_list(request):
    qs = Listing.objects.filter(is_active=True).select_related('state', 'district', 'category', 'user')
    paginator = Paginator(qs.order_by('-is_featured', '-created_at'), 24)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'listings/list.html', {'page_obj': page_obj})


def listing_detail(request, pk: int):
    item = get_object_or_404(Listing.objects.select_related('state', 'district', 'category', 'user').prefetch_related('images'), pk=pk)
    return render(request, 'listings/detail.html', {'item': item})


@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing: Listing = form.save(commit=False)
            listing.user = request.user
            listing.ai_genuine_score = score_genuineness(listing)
            listing.is_featured = listing.ai_genuine_score >= 0.7
            listing.save()
            for f in request.FILES.getlist('images'):
                ListingImage.objects.create(listing=listing, image=f)
            return redirect(listing.get_absolute_url())
    else:
        form = ListingForm()
    return render(request, 'listings/create.html', {'form': form})


def score_genuineness(listing: Listing) -> float:
    # Placeholder lightweight AI heuristic: boosts genuine listings by completeness and description quality
    score = 0.3
    if len(listing.description) > 120:
        score += 0.25
    if listing.price and listing.price > 0:
        score += 0.15
    if listing.address:
        score += 0.1
    if listing.title and len(listing.title.split()) >= 3:
        score += 0.1
    return min(score, 1.0)


# Create your views here.
