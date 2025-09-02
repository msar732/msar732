from django.contrib.sitemaps import Sitemap
from .models import Listing


class ListingSitemap(Sitemap):
	changefreq = "daily"
	priority = 0.7

	def items(self):
		return Listing.objects.filter(is_active=True, is_verified_ai=True).only("slug", "updated_at")

	def lastmod(self, obj: Listing):
		return obj.updated_at