from django.urls import path
from django.views.generic import TemplateView

app_name = 'food_beverage'

urlpatterns = [
    path('', TemplateView.as_view(template_name='food_beverage/home.html'), name='home'),
]
