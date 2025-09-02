from django.urls import path
from django.views.generic import TemplateView

app_name = 'sports_leisure'

urlpatterns = [
    path('', TemplateView.as_view(template_name='sports_leisure/home.html'), name='home'),
]
