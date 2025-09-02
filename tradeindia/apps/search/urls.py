"""
URL configuration for search app
"""
from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Search views
    path('', views.ListingSearchView.as_view(), name='listing_search'),
    path('autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
    
    # Saved searches
    path('saved/', views.SavedSearchListView.as_view(), name='saved_searches'),
    path('save/', views.save_search, name='save_search'),
    path('saved/<int:pk>/delete/', views.delete_saved_search, name='delete_saved_search'),
    path('saved/<int:pk>/toggle-alert/', views.toggle_search_alert, name='toggle_search_alert'),
    
    # Analytics (admin only)
    path('analytics/', views.SearchAnalyticsView.as_view(), name='analytics'),
]