from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.http import JsonResponse
from django.db.models import Q
from django.core.cache import cache
from .models import Listing
from .forms import ListingForm


class HomeView(TemplateView):
	template_name = "home.html"


class ListingListView(ListView):
	model = Listing
	template_name = "listings/list.html"
	paginate_by = 24

	def get_queryset(self):
		qs = Listing.objects.filter(is_active=True)
		# Default: show only genuine/verified items
		qs = qs.filter(is_verified_ai=True).order_by("-ai_genuineness_score", "-created_at")
		q = self.request.GET.get("q")
		state = self.request.GET.get("state")
		district = self.request.GET.get("district")
		if q:
			qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(city__icontains=q))
		if state:
			qs = qs.filter(state__iexact=state)
		if district:
			qs = qs.filter(district__iexact=district)
		return qs.select_related("category", "owner").prefetch_related("images")


class ListingDetailView(DetailView):
	model = Listing
	template_name = "listings/detail.html"
	slug_field = "slug"
	slug_url_kwarg = "slug"

	def get_queryset(self):
		return Listing.objects.filter(is_active=True).select_related("category", "owner").prefetch_related("images")


class ListingCreateView(LoginRequiredMixin, CreateView):
	model = Listing
	form_class = ListingForm
	template_name = "listings/create.html"

	def form_valid(self, form: ListingForm):
		listing = form.save(owner=self.request.user)
		# naive AI genuineness score baseline
		listing.ai_genuineness_score = compute_ai_genuineness_score(listing)
		listing.is_verified_ai = listing.ai_genuineness_score >= 0.6
		listing.save(update_fields=["ai_genuineness_score", "is_verified_ai"])
		self.object = listing
		return redirect(listing.get_absolute_url())


# Simple heuristic; in production replace with proper model
KEYWORDS_SUSPICIOUS = {"loan approval instantly", "no documents", "first come", "whatsapp only", "forex", "crypto"}


def compute_ai_genuineness_score(listing: Listing) -> float:
	score = 0.7
	txt = f"{listing.title} {listing.description}".lower()
	for bad in KEYWORDS_SUSPICIOUS:
		if bad in txt:
			score -= 0.2
	if listing.images.count() == 0:
		score -= 0.3
	if len(listing.description) < 50:
		score -= 0.1
	return max(0.0, min(1.0, score))


def api_featured(request):
	cache_key = "api_featured_v1"
	data = cache.get(cache_key)
	if data is None:
		qs = Listing.objects.filter(is_active=True, is_verified_ai=True).order_by("-ai_genuineness_score", "-created_at")[0:12]
		data = []
		for l in qs:
			img = l.images.first().image.url if l.images.exists() else "/static/placeholder.jpg"
			data.append({
				"slug": l.slug,
				"title": l.title,
				"category": l.category.name,
				"thumbnail": img,
				"location": l.location_display,
			})
		cache.set(cache_key, data, 120)
	return JsonResponse(data, safe=False)