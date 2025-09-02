from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'search'

router = DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.SearchView.as_view(), name='search'),
    path('suggestions/', views.SearchSuggestionsView.as_view(), name='suggestions'),
    path('popular/', views.PopularSearchesView.as_view(), name='popular'),
    path('save/', views.SaveSearchView.as_view(), name='save_search'),
    path('saved/', views.SavedSearchesView.as_view(), name='saved_searches'),
]