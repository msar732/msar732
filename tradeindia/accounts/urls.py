from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('my-listings/', views.MyListingsView.as_view(), name='my_listings'),
    path('verify/', views.VerificationView.as_view(), name='verify'),
]