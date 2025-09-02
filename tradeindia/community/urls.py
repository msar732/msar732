from django.urls import path
from django.views.generic import TemplateView

app_name = 'community'

urlpatterns = [
    path('', TemplateView.as_view(template_name='community/home.html'), name='home'),
]