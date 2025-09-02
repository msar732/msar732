"""
URL configuration for core app
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Categories and Locations
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('locations/', views.LocationsView.as_view(), name='locations'),
    
    # Static pages
    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    
    # User dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # AJAX endpoints
    path('ajax/districts/', views.get_districts, name='ajax_districts'),
    path('ajax/cities/', views.get_cities, name='ajax_cities'),
    path('ajax/subcategories/', views.get_subcategories, name='ajax_subcategories'),
]