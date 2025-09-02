from django.urls import path
from . import views

app_name = "listings"

urlpatterns = [
	path("", views.ListingListView.as_view(), name="list"),
	path("create/", views.ListingCreateView.as_view(), name="create"),
	path("<slug:slug>/", views.ListingDetailView.as_view(), name="detail"),
	# API
	path("api/featured/", views.api_featured, name="api_featured"),
]