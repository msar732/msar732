from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, CategoryViewSet, StateViewSet, DistrictViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'states', StateViewSet)
router.register(r'districts', DistrictViewSet)

urlpatterns = [
    path('', include(router.urls)),
]