from django.urls import path
from . import views

urlpatterns = [
    path('locations.json', views.locations_json, name='locations_json'),
]

