from django.urls import path
from django.views.generic import TemplateView

app_name = 'home_living'

urlpatterns = [
    path('', TemplateView.as_view(template_name='home_living/home.html'), name='home'),
]
