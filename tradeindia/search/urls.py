# Search URLs
from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('suggestions/', views.search_suggestions, name='suggestions'),
    path('advanced/', views.advanced_search, name='advanced'),
]