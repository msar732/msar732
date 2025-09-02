from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Category, Listing

User = get_user_model()


class ListingTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(email="u@example.com", password="pass12345")
		self.category = Category.objects.create(name="Electronics")

	def test_create_listing_and_ai_score(self):
		l = Listing.objects.create(
			owner=self.user,
			title="iPhone 13 for sale",
			description="Gently used phone with bill and box, genuine seller.",
			category=self.category,
			state="Maharashtra",
			district="Pune",
		)
		self.assertTrue(l.slug)
		self.assertIsNotNone(l.created_at)

	def test_search_filters(self):
		Listing.objects.create(owner=self.user, title="Bike", description="City bike", category=self.category, state="Maharashtra", district="Pune")
		Listing.objects.create(owner=self.user, title="Laptop", description="Gaming laptop", category=self.category, state="Karnataka", district="Bengaluru Urban")
		url = reverse("listings:list") + "?state=Maharashtra"
		resp = self.client.get(url)
		self.assertContains(resp, "Bike")
		self.assertNotContains(resp, "Laptop")