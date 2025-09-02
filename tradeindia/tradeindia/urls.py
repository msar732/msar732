"""
URL configuration for tradeindia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/listings/', include('listings.urls')),
    path('api/search/', include('search.urls')),
    path('api/locations/', include('locations.urls')),
    path('', HomeView.as_view(), name='home'),
    path('listings/', include('listings.urls', namespace='listings_web')),
    path('search/', include('search.urls', namespace='search_web')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
