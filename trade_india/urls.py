from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from listings.views import HomeView
from listings.sitemaps import ListingSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {"listings": ListingSitemap}

urlpatterns = [
	path("admin/", admin.site.urls),
	path("accounts/", include("allauth.urls")),
	path("", HomeView.as_view(), name="home"),
	path("listings/", include("listings.urls")),
	path("locations/", include("locations.urls")),
	path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
	path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)