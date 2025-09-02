from django.urls import path
from django.views.generic import TemplateView

app_name = 'business'

urlpatterns = [
    path('', TemplateView.as_view(template_name='business/home.html'), name='home'),
]
