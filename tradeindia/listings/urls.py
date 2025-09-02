from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.ListingHomeView.as_view(), name='home'),
    path('create/', views.CreateListingView.as_view(), name='create'),
    path('detail/<uuid:listing_id>/', views.ListingDetailView.as_view(), name='detail'),
]