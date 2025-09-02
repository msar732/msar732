from django.urls import path
from django.views.generic import TemplateView

app_name = 'services'

urlpatterns = [
    path('', TemplateView.as_view(template_name='services/home.html'), name='home'),
]