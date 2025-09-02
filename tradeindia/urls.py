# Trade India Main URLs
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('listings/', include('listings.urls')),
    path('search/', include('search.urls')),
    path('api/', include('api.urls')),
    
    # Main category pages
    path('motors/', include('motors.urls')),
    path('property/', include('property.urls')),
    path('jobs/', include('jobs.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('services/', include('services.urls')),
    path('community/', include('community.urls')),
    
    # Electronics & Technology
    path('mobile-phones/', include('mobile_phones.urls')),
    path('electronics/', include('electronics.urls')),
    
    # Fashion & Lifestyle
    path('fashion/', include('fashion.urls')),
    path('health-beauty/', include('health_beauty.urls')),
    
    # Home & Garden
    path('home-living/', include('home_living.urls')),
    path('antiques-collectibles/', include('antiques_collectibles.urls')),
    
    # Sports & Recreation
    path('sports-leisure/', include('sports_leisure.urls')),
    path('books-music/', include('books_music.urls')),
    
    # Family
    path('baby-kids/', include('baby_kids.urls')),
    path('pets/', include('pets.urls')),
    
    # Business & Industry
    path('business/', include('business.urls')),
    path('farming-outdoors/', include('farming_outdoors.urls')),
    
    # Food & Travel
    path('food-beverage/', include('food_beverage.urls')),
    path('travel/', include('travel.urls')),
    
    # Auctions & Special
    path('auctions/', include('auctions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)