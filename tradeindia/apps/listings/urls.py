"""
URL configuration for listings app
"""
from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Listing views
    path('', views.ListingListView.as_view(), name='list'),
    path('category/<slug:category_slug>/', views.ListingListView.as_view(), name='category_detail'),
    path('create/', views.ListingCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.ListingDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ListingUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', views.ListingDeleteView.as_view(), name='delete'),
    
    # User listings
    path('my/listings/', views.MyListingsView.as_view(), name='my_listings'),
    path('my/favorites/', views.FavoriteListingsView.as_view(), name='favorites'),
    
    # AJAX endpoints
    path('ajax/<uuid:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('ajax/<uuid:pk>/report/', views.report_listing, name='report'),
    path('ajax/<uuid:pk>/sold/', views.mark_as_sold, name='mark_sold'),
    path('ajax/attributes/', views.get_attributes, name='get_attributes'),
]