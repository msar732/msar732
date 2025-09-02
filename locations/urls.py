from django.urls import path
from . import views

app_name = "locations"

urlpatterns = [
	path("api/states_districts/", views.api_states_districts, name="api_states_districts"),
]