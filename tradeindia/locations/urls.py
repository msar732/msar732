from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'states', views.StateViewSet, basename='state')
router.register(r'districts', views.DistrictViewSet, basename='district')
router.register(r'cities', views.CityViewSet, basename='city')

urlpatterns = [
    path('', include(router.urls)),
    path('states/', views.StateListView.as_view(), name='states'),
    path('districts/<int:state_id>/', views.DistrictListView.as_view(), name='districts'),
    path('cities/<int:district_id>/', views.CityListView.as_view(), name='cities'),
]