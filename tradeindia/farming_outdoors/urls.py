from django.urls import path
from django.views.generic import TemplateView

app_name = 'farming_outdoors'

urlpatterns = [
    path('', TemplateView.as_view(template_name='farming_outdoors/home.html'), name='home'),
]
