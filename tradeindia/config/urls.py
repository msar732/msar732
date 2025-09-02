"""
TradeIndia URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from two_factor.urls import urlpatterns as tf_urls
from apps.core.sitemaps import StaticViewSitemap, ListingSitemap, CategorySitemap

# Sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'listings': ListingSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    
    # Two-factor authentication
    path('account/two-factor/', include(tf_urls)),
    
    # Authentication URLs
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    
    # OAuth2 Provider
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # Core app URLs
    path('', include('apps.core.urls')),
    
    # App-specific URLs
    path('listings/', include('apps.listings.urls')),
    path('search/', include('apps.search.urls')),
    path('ai/', include('apps.ai_verification.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('payments/', include('apps.payments.urls')),
    path('messages/', include('django_messages.urls')),
    
    # API URLs
    path('api/v1/', include('apps.api.urls')),
    
    # Third-party app URLs
    path('activity/', include('actstream.urls')),
    path('select2/', include('django_select2.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('rosetta/', include('rosetta.urls')),
    
    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Robots.txt
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Silk profiler
if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
handler403 = 'apps.core.views.error_403'
handler400 = 'apps.core.views.error_400'

# Admin site customization
admin.site.site_header = 'TradeIndia Administration'
admin.site.site_title = 'TradeIndia Admin'
admin.site.index_title = 'Welcome to TradeIndia Administration'