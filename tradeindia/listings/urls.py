from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.listing_list, name='list'),
    path('<uuid:pk>/', views.listing_detail, name='detail'),
    path('create/', views.create_listing, name='create'),
    path('<uuid:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('api/districts/', views.get_districts, name='get_districts'),
]