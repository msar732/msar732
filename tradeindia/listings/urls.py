from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'listings'

router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename='listing')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'inquiries', views.InquiryViewSet, basename='inquiry')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.ListingListView.as_view(), name='list'),
    path('create/', views.ListingCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.ListingEditView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.ListingDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/favorite/', views.FavoriteToggleView.as_view(), name='favorite_toggle'),
    path('<uuid:pk>/inquiry/', views.InquiryCreateView.as_view(), name='inquiry_create'),
    path('<uuid:pk>/report/', views.ReportCreateView.as_view(), name='report'),
    path('category/<slug:slug>/', views.CategoryListingView.as_view(), name='category'),
    path('featured/', views.FeaturedListingsView.as_view(), name='featured'),
]