from django.shortcuts import render
from listings.models import Listing, Category
from django.core.paginator import Paginator


def home(request):
    query = request.GET.get('q', '')
    state_id = request.GET.get('state')
    district_id = request.GET.get('district')
    category_slug = request.GET.get('category')

    listings = Listing.objects.filter(is_active=True).select_related(
        'state', 'district', 'category', 'user'
    ).prefetch_related('images')

    if query:
        listings = listings.search(query)
    if state_id:
        listings = listings.filter(state_id=state_id)
    if district_id:
        listings = listings.filter(district_id=district_id)
    if category_slug:
        listings = listings.filter(category__slug=category_slug)

    listings = listings.order_by('-is_featured', '-created_at')

    paginator = Paginator(listings, 24)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'core/home.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'query': query,
    })


# Create your views here.
