from django.urls import path
from django.views.generic import TemplateView

app_name = 'travel'

urlpatterns = [
    path('', TemplateView.as_view(template_name='travel/home.html'), name='home'),
]
